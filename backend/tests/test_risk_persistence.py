"""
Tests for Risk Persistence Service
================================
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def get_auth_headers():
    """Get auth headers using seeded admin credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@airiskmanager.com", "password": "RiskoraDemo123!"},
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {}


def get_any_user_headers():
    """Get auth headers using any valid user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@airiskmanager.com", "password": "RiskoraDemo123!"},
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {}


class TestRiskPersistenceService:
    """Tests for risk persistence service."""

    def test_create_and_retrieve_assessment(self):
        """Test creating a transaction, performing assessment, and retrieving it."""
        headers = get_auth_headers()
        assert headers, "Failed to get auth headers"

        from app.db.database import SessionLocal
        from app.models import Transaction, RiskAssessment, TriggeredRule, SHAPFeature
        from app.services import risk_persistence_service

        db = SessionLocal()
        try:
            tx = db.query(Transaction).first()
            if not tx:
                pytest.skip("No transactions in database")

            tx_id = tx.id

            inference_result = {
                "risk_score": 42.5,
                "risk_level": "MEDIUM",
                "decision": "REVIEW",
                "ml_probability": 0.425,
                "ml_score": 42.5,
                "rule_score": 30.0,
                "explanation": "Test persistence",
                "model_version": "risk_model_v1",
                "preprocessor_version": "v1",
                "triggered_rules": [
                    {
                        "rule_id": "RULE_TEST",
                        "name": "Test Rule",
                        "severity": "MEDIUM",
                        "score_contribution": 10,
                        "triggered": True,
                        "reason": "Test reason",
                    }
                ],
                "top_positive_features": [
                    {"feature_name": "amount", "shap_value": 0.3, "direction": "increases_risk"}
                ],
                "top_negative_features": [
                    {"feature_name": "card2", "shap_value": -0.2, "direction": "decreases_risk"}
                ],
            }

            assessment, rules, shap_feats = risk_persistence_service.create_risk_assessment(
                db, tx_id, inference_result
            )
            db.commit()

            assert assessment.id is not None
            assert assessment.transaction_id == tx_id
            assert assessment.risk_score == 43
            assert assessment.ml_probability == 0.425
            assert len(rules) == 1
            assert len(shap_feats) == 2

            latest = risk_persistence_service.get_latest_risk_assessment(db, tx_id)
            assert latest is not None
            assert latest.id == assessment.id

            history = risk_persistence_service.get_risk_history(db, tx_id, limit=10)
            assert len(history) >= 1

            db.query(TriggeredRule).filter(TriggeredRule.risk_assessment_id == assessment.id).delete()
            db.query(SHAPFeature).filter(SHAPFeature.risk_assessment_id == assessment.id).delete()
            db.query(RiskAssessment).filter(RiskAssessment.id == assessment.id).delete()
            db.commit()

        finally:
            db.close()

    def test_create_risk_event(self):
        """Test creating a risk event."""
        headers = get_auth_headers()
        assert headers

        from app.db.database import SessionLocal
        from app.models import Transaction, RiskEvent
        from app.services import risk_persistence_service

        db = SessionLocal()
        try:
            tx = db.query(Transaction).first()
            if not tx:
                pytest.skip("No transactions in database")

            event = risk_persistence_service.create_risk_event(
                db,
                transaction_id=tx.id,
                event_type="RISK_ASSESSED",
                description="Test event",
                severity="INFO",
            )
            db.commit()

            assert event.id is not None
            assert event.transaction_id == tx.id

            saved = db.query(RiskEvent).filter(RiskEvent.id == event.id).first()
            assert saved is not None

            db.query(RiskEvent).filter(RiskEvent.id == event.id).delete()
            db.commit()

        finally:
            db.close()

    def test_get_latest_assessment_empty(self):
        """Test getting latest assessment when none exists."""
        from app.db.database import SessionLocal
        from app.services import risk_persistence_service

        db = SessionLocal()
        try:
            result = risk_persistence_service.get_latest_risk_assessment(db, 999999)
            assert result is None
        finally:
            db.close()

    def test_get_risk_history_empty(self):
        """Test getting history when none exists."""
        from app.db.database import SessionLocal
        from app.services import risk_persistence_service

        db = SessionLocal()
        try:
            history = risk_persistence_service.get_risk_history(db, 999999, limit=10)
            assert len(history) == 0
        finally:
            db.close()


class TestIEEERiskAPIPersistence:
    """API tests for risk persistence."""

    def test_assess_and_persist(self):
        """Test POST /api/v1/risk/assess with transaction_id persists."""
        headers = get_auth_headers()
        assert headers, "Failed to get auth headers"

        from app.db.database import SessionLocal
        from app.models import Transaction

        db = SessionLocal()
        try:
            tx = db.query(Transaction).first()
            if not tx:
                pytest.skip("No transactions in database")

            response = client.post(
                "/api/v1/risk/assess",
                params={"transaction_id": tx.id, "persist": "true"},
                json={
                    "TransactionAmt": tx.amount,
                    "TransactionDT": 86400,
                    "ProductCD": "C",
                    "card1": 100.0,
                    "card2": 200.0,
                },
                headers=headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert "risk_score" in data
            assert "risk_level" in data

            from app.models import RiskAssessment
            assessment = db.query(RiskAssessment).filter(
                RiskAssessment.transaction_id == tx.id
            ).order_by(RiskAssessment.id.desc()).first()

            assert assessment is not None, "Assessment was not persisted"
            assert abs(assessment.ml_probability - data["ml_probability"]) < 0.01

            db.query(RiskAssessment).filter(RiskAssessment.id == assessment.id).delete()
            db.commit()

        finally:
            db.close()

    def test_assess_without_persist(self):
        """Test POST /api/v1/risk/assess without transaction_id does not persist."""
        headers = get_auth_headers()
        assert headers

        from app.db.database import SessionLocal
        from app.models import RiskAssessment
        from sqlalchemy import func

        db = SessionLocal()
        try:
            count_before = db.query(func.count(RiskAssessment.id)).scalar()

            response = client.post(
                "/api/v1/risk/assess",
                json={
                    "TransactionAmt": 100.0,
                    "TransactionDT": 86400,
                },
                headers=headers,
            )

            assert response.status_code == 200

            count_after = db.query(func.count(RiskAssessment.id)).scalar()
            assert count_after == count_before

        finally:
            db.close()

    def test_get_latest_assessment(self):
        """Test GET /api/v1/risk/transactions/{id} returns latest assessment."""
        headers = get_auth_headers()
        assert headers

        from app.db.database import SessionLocal
        from app.models import Transaction, RiskAssessment

        db = SessionLocal()
        try:
            tx = db.query(Transaction).first()
            if not tx:
                pytest.skip("No transactions in database")

            assessment = db.query(RiskAssessment).filter(
                RiskAssessment.transaction_id == tx.id
            ).order_by(RiskAssessment.id.desc()).first()

            response = client.get(
                f"/api/v1/risk/transactions/{tx.id}",
                headers=headers,
            )

            if assessment:
                assert response.status_code == 200
                data = response.json()
                assert data["transaction_id"] == tx.id
                assert "risk_score" in data
                assert "triggered_rules" in data
            else:
                assert response.status_code == 404

        finally:
            db.close()

    def test_get_latest_assessment_not_found(self):
        """Test GET /api/v1/risk/transactions/{id} returns 404 when not found."""
        headers = get_auth_headers()
        assert headers

        response = client.get(
            "/api/v1/risk/transactions/999999",
            headers=headers,
        )

        assert response.status_code == 404

    def test_get_risk_history(self):
        """Test GET /api/v1/risk/transactions/{id}/history returns history."""
        headers = get_auth_headers()
        assert headers

        from app.db.database import SessionLocal
        from app.models import Transaction

        db = SessionLocal()
        try:
            tx = db.query(Transaction).first()
            if not tx:
                pytest.skip("No transactions in database")

            response = client.get(
                f"/api/v1/risk/transactions/{tx.id}/history",
                headers=headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["transaction_id"] == tx.id
            assert "assessments" in data
            assert "total" in data

        finally:
            db.close()

    def test_get_risk_events(self):
        """Test GET /api/v1/risk/transactions/{id}/events returns events."""
        headers = get_auth_headers()
        assert headers

        from app.db.database import SessionLocal
        from app.models import Transaction

        db = SessionLocal()
        try:
            tx = db.query(Transaction).first()
            if not tx:
                pytest.skip("No transactions in database")

            response = client.get(
                f"/api/v1/risk/transactions/{tx.id}/events",
                headers=headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["transaction_id"] == tx.id
            assert "events" in data
            assert "total" in data

        finally:
            db.close()

    def test_unauthorized_access(self):
        """Test that unauthorized requests are rejected."""
        response = client.get("/api/v1/risk/transactions/1")
        assert response.status_code == 403

    def test_health_endpoint(self):
        """Test GET /api/v1/risk/health works."""
        response = client.get("/api/v1/risk/health")
        assert response.status_code in (200, 503)

    def test_inference_only_mode(self):
        """Test that inference-only mode works without persistence."""
        headers = get_auth_headers()
        assert headers

        response = client.post(
            "/api/v1/risk/assess",
            json={
                "TransactionAmt": 75.0,
                "TransactionDT": 86400 * 2,
                "ProductCD": "C",
                "card1": 150.0,
                "card2": 250.0,
            },
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["risk_score"] >= 0
        assert data["risk_level"] in ("LOW", "MEDIUM", "HIGH")
        assert data["decision"] in ("ALLOW", "REVIEW", "BLOCK")
