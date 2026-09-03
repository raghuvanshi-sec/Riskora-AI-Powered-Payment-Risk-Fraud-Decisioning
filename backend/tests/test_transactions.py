"""Transaction API tests using the in-memory SQLite override pattern.

Covers creation, retrieval, filtering, sorting, pagination, authz,
validation, and the immutability/PATCH contract.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.user import User
from app.models.merchant import Merchant
from app.models.transaction import Transaction
from app.core.security import get_password_hash
from app.main import app
from app.db.database import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _override_db():
    # Set the SQLite override only for this module's tests; clear it afterwards
    # so it does not leak into other test modules (e.g. test_auth).
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _mk_user(db, email, name, role):
    u = User(
        email=email,
        password_hash=get_password_hash("secure-password"),
        name=name,
        role=role,
        is_active=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u.id


def _mk_merchant(db, name="Acme", category="Retail", risk_level="LOW"):
    m = Merchant(
        name=name, category=category, risk_level=risk_level, is_active=True
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m.id


@pytest.fixture
def analyst():
    db = TestingSessionLocal()
    uid = _mk_user(db, "analyst@example.com", "Risk Analyst", "RISK_ANALYST")
    db.close()
    return uid


@pytest.fixture
def admin():
    db = TestingSessionLocal()
    uid = _mk_user(db, "admin@example.com", "Admin", "ADMIN")
    db.close()
    return uid


@pytest.fixture
def viewer():
    db = TestingSessionLocal()
    uid = _mk_user(db, "viewer@example.com", "Viewer", "USER")
    db.close()
    return uid


@pytest.fixture
def data():
    db = TestingSessionLocal()
    user_id = _mk_user(db, "u1@example.com", "User One", "RISK_ANALYST")
    merchant_id = _mk_merchant(db, "Acme", "Retail", "LOW")
    db.close()
    return {"user_id": user_id, "merchant_id": merchant_id}


def _token(client, email, password="secure-password"):
    r = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _tx_body(user_id, merchant_id, ref="TX-10000", amount=1000.0):
    return {
        "transaction_reference": ref,
        "user_id": user_id,
        "merchant_id": merchant_id,
        "amount": amount,
        "currency": "INR",
        "transaction_timestamp": "2026-08-30T10:00:00Z",
    }


client = TestClient(app)


def test_create_transaction(data, analyst):
    token = _token(client, "analyst@example.com")
    r = client.post(
        "/api/v1/transactions",
        json=_tx_body(data["user_id"], data["merchant_id"]),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201, r.text
    d = r.json()
    assert d["transaction_reference"] == "TX-10000"
    assert d["amount"] == 1000.0
    assert d["user"]["id"] == data["user_id"]
    assert d["merchant"]["id"] == data["merchant_id"]
    assert d["risk_score"] is None
    assert d["risk_level"] is None
    assert d["decision"] is None


def test_create_transaction_requires_analyst_or_admin(data, viewer):
    token = _token(client, "viewer@example.com")
    r = client.post(
        "/api/v1/transactions",
        json=_tx_body(data["user_id"], data["merchant_id"]),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_create_transaction_rejects_duplicate_reference(data, analyst):
    token = _token(client, "analyst@example.com")
    body = _tx_body(data["user_id"], data["merchant_id"])
    assert (
        client.post(
            "/api/v1/transactions",
            json=body,
            headers={"Authorization": f"Bearer {token}"},
        ).status_code
        == 201
    )
    r = client.post(
        "/api/v1/transactions",
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 400


def test_create_transaction_rejects_invalid_fk(analyst):
    token = _token(client, "analyst@example.com")
    r = client.post(
        "/api/v1/transactions",
        json=_tx_body(99999, 99999),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 400


def test_list_transactions_pagination(data, analyst):
    token = _token(client, "analyst@example.com")
    for i in range(5):
        client.post(
            "/api/v1/transactions",
            json=_tx_body(data["user_id"], data["merchant_id"], ref=f"TX-P{i}"),
            headers={"Authorization": f"Bearer {token}"},
        )
    r = client.get(
        "/api/v1/transactions?page=1&page_size=2",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["page"] == 1
    assert d["page_size"] == 2
    assert len(d["items"]) == 2
    assert d["total"] == 5
    assert d["total_pages"] == 3


def test_list_transactions_search_by_user(data, analyst):
    token = _token(client, "analyst@example.com")
    client.post(
        "/api/v1/transactions",
        json=_tx_body(data["user_id"], data["merchant_id"], ref="TX-S1"),
        headers={"Authorization": f"Bearer {token}"},
    )
    r = client.get(
        "/api/v1/transactions?search=User",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["total"] == 1


def test_list_transactions_sort_desc(data, analyst):
    token = _token(client, "analyst@example.com")
    for i, amt in enumerate([100.0, 500.0, 300.0]):
        client.post(
            "/api/v1/transactions",
            json=_tx_body(
                data["user_id"], data["merchant_id"], ref=f"TX-S{i}", amount=amt
            ),
            headers={"Authorization": f"Bearer {token}"},
        )
    r = client.get(
        "/api/v1/transactions?sort_by=amount&sort_order=desc&page_size=3",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    amounts = [it["amount"] for it in r.json()["items"]]
    assert amounts == [500.0, 300.0, 100.0]


def test_list_transactions_invalid_sort(analyst):
    token = _token(client, "analyst@example.com")
    r = client.get(
        "/api/v1/transactions?sort_by=hack",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 400


def test_get_transaction_detail(data, analyst):
    token = _token(client, "analyst@example.com")
    create = client.post(
        "/api/v1/transactions",
        json=_tx_body(data["user_id"], data["merchant_id"]),
        headers={"Authorization": f"Bearer {token}"},
    )
    tx_id = create.json()["id"]
    r = client.get(
        f"/api/v1/transactions/{tx_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["id"] == tx_id
    assert "risk_assessments" in d
    assert "risk_events" in d
    assert d["risk_assessments"] == []
    assert d["risk_events"] == []


def test_get_transaction_404(analyst):
    token = _token(client, "analyst@example.com")
    r = client.get(
        "/api/v1/transactions/99999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404


def test_patch_transaction(data, analyst):
    token = _token(client, "analyst@example.com")
    create = client.post(
        "/api/v1/transactions",
        json=_tx_body(data["user_id"], data["merchant_id"]),
        headers={"Authorization": f"Bearer {token}"},
    )
    tx_id = create.json()["id"]
    r = client.patch(
        f"/api/v1/transactions/{tx_id}",
        json={"location": "Mumbai"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["location"] == "Mumbai"


def test_patch_rejects_immutable_fields(data, analyst):
    token = _token(client, "analyst@example.com")
    create = client.post(
        "/api/v1/transactions",
        json=_tx_body(data["user_id"], data["merchant_id"], amount=500.0),
        headers={"Authorization": f"Bearer {token}"},
    )
    tx_id = create.json()["id"]
    # amount/transaction_reference are absent from TransactionUpdate, so the
    # PATCH is a no-op for those fields -- they must remain unchanged.
    r = client.patch(
        f"/api/v1/transactions/{tx_id}",
        json={"amount": 999999.0, "transaction_reference": "NOPE",
              "location": "Mumbai"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["amount"] == 500.0
    assert d["transaction_reference"] == "TX-10000"
    assert d["location"] == "Mumbai"


def test_list_requires_auth():
    r = client.get("/api/v1/transactions")
    assert r.status_code in (401, 403)


def test_get_summary(data, analyst):
    token = _token(client, "analyst@example.com")
    client.post(
        "/api/v1/transactions",
        json=_tx_body(data["user_id"], data["merchant_id"]),
        headers={"Authorization": f"Bearer {token}"},
    )
    r = client.get(
        "/api/v1/transactions/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["total_transactions"] == 1
    assert d["total_amount"] == 1000.0
