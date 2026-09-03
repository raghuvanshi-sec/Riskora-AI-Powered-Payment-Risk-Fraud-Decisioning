import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.base import Base
from app.models.user import User
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

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    db = TestingSessionLocal()
    user = User(
        email="analyst@example.com",
        password_hash=get_password_hash("secure-password"),
        name="Risk Analyst",
        role="RISK_ANALYST",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com", "password": "secure-password", "name": "New User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "password_hash" not in data
    assert "password" not in data

def test_login_user(test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "analyst@example.com", "password": "secure-password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "analyst@example.com"

def test_login_user_invalid(test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "analyst@example.com", "password": "wrong-password"}
    )
    assert response.status_code == 400

def test_me(test_user):
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "analyst@example.com", "password": "secure-password"}
    )
    token = login_res.json()["access_token"]
    
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "analyst@example.com"
