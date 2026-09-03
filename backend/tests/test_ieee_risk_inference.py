"""
Tests for IEEE-CIS Risk Inference Service
========================================
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.ieee_risk_service import (
    IEEE_CIS_RuleEngine,
    IEEERiskService,
    get_ieee_risk_service,
)


client = TestClient(app)


def get_auth_headers():
    """Get auth headers for testing."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@airiskmanager.com", "password": "RiskoraDemo123!"},
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {}


class TestIEEE_CIS_RuleEngine:
    """Unit tests for IEEE-CIS rule engine."""

    def test_high_amount_rule_triggers(self):
        """High transaction amount should trigger rule."""
        engine = IEEE_CIS_RuleEngine()
        transaction = {
            "amount": 500.0,
            "amount_log": 6.2,
            "transaction_hour": 12,
            "P_emaildomain": "gmail.com",
            "R_emaildomain": "gmail.com",
            "device_type_present": 1,
            "device_info_present": 1,
            "card2": 1.0,
            "card3": 1.0,
            "product_code": "C",
        }

        score, rules = engine.evaluate(transaction)

        assert score > 0
        high_amount_rule = next(r for r in rules if r["rule_id"] == "RULE_HIGH_AMOUNT")
        assert high_amount_rule["triggered"] is True

    def test_low_amount_no_high_rule(self):
        """Low transaction amount should not trigger high amount rule."""
        engine = IEEE_CIS_RuleEngine()
        transaction = {
            "amount": 50.0,
            "amount_log": 3.9,
            "transaction_hour": 12,
            "P_emaildomain": "gmail.com",
            "R_emaildomain": "gmail.com",
            "device_type_present": 1,
            "device_info_present": 1,
            "card2": 1.0,
            "card3": 1.0,
            "product_code": "C",
        }

        score, rules = engine.evaluate(transaction)

        high_amount_rule = next(r for r in rules if r["rule_id"] == "RULE_HIGH_AMOUNT")
        assert high_amount_rule["triggered"] is False

    def test_unusual_hour_rule(self):
        """Transaction at 2am should trigger unusual hour rule."""
        engine = IEEE_CIS_RuleEngine()
        transaction = {
            "amount": 100.0,
            "amount_log": 4.6,
            "transaction_hour": 2,
            "P_emaildomain": "gmail.com",
            "R_emaildomain": "gmail.com",
            "device_type_present": 1,
            "device_info_present": 1,
            "card2": 1.0,
            "card3": 1.0,
            "product_code": "C",
        }

        score, rules = engine.evaluate(transaction)

        hour_rule = next(r for r in rules if r["rule_id"] == "RULE_UNUSUAL_HOUR")
        assert hour_rule["triggered"] is True

    def test_email_mismatch_rule(self):
        """Different billing and recipient email should trigger rule."""
        engine = IEEE_CIS_RuleEngine()
        transaction = {
            "amount": 100.0,
            "amount_log": 4.6,
            "transaction_hour": 12,
            "P_emaildomain": "gmail.com",
            "R_emaildomain": "yahoo.com",
            "device_type_present": 1,
            "device_info_present": 1,
            "card2": 1.0,
            "card3": 1.0,
            "product_code": "C",
        }

        score, rules = engine.evaluate(transaction)

        email_rule = next(r for r in rules if r["rule_id"] == "RULE_EMAIL_MISMATCH")
        assert email_rule["triggered"] is True

    def test_missing_device_rule(self):
        """Missing device info should trigger rule."""
        engine = IEEE_CIS_RuleEngine()
        transaction = {
            "amount": 100.0,
            "amount_log": 4.6,
            "transaction_hour": 12,
            "P_emaildomain": "gmail.com",
            "R_emaildomain": "gmail.com",
            "device_type_present": 0,
            "device_info_present": 0,
            "card2": 1.0,
            "card3": 1.0,
            "product_code": "C",
        }

        score, rules = engine.evaluate(transaction)

        device_rule = next(r for r in rules if r["rule_id"] == "RULE_MISSING_DEVICE")
        assert device_rule["triggered"] is True

    def test_score_capped_at_100(self):
        """Rule score should be capped at 100."""
        engine = IEEE_CIS_RuleEngine()
        transaction = {
            "amount": 10000.0,
            "amount_log": 9.2,
            "transaction_hour": 2,
            "P_emaildomain": None,
            "R_emaildomain": "yahoo.com",
            "device_type_present": 0,
            "device_info_present": 0,
            "card2": None,
            "card3": None,
            "product_code": "W",
        }

        score, rules = engine.evaluate(transaction)

        assert score <= 100


class TestIEEERiskService:
    """Integration tests for IEEE risk service."""

    def test_service_is_singleton(self):
        """Service should return same instance."""
        service1 = get_ieee_risk_service()
        service2 = get_ieee_risk_service()
        assert service1 is service2

    def test_health_check_structure(self):
        """Health check should return expected structure."""
        service = get_ieee_risk_service()
        health = service.health_check()

        assert "status" in health
        assert "model_loaded" in health
        assert "preprocessor_loaded" in health

    def test_assess_returns_expected_fields(self):
        """Assess should return all expected fields."""
        service = get_ieee_risk_service()

        if service.model is None:
            pytest.skip("Model not loaded")

        transaction = {
            "TransactionAmt": 150.0,
            "TransactionDT": 86400 * 3,
            "ProductCD": "C",
            "card1": 100.0,
            "card2": 200.0,
            "card3": 300.0,
            "card4": "visa",
            "card5": 500.0,
            "card6": "credit",
            "P_emaildomain": "gmail.com",
            "R_emaildomain": "gmail.com",
            "DeviceType": "desktop",
            "DeviceInfo": "Chrome on Windows",
        }

        result = service.assess(transaction)

        assert "risk_score" in result
        assert "risk_level" in result
        assert "decision" in result
        assert "ml_probability" in result
        assert "ml_score" in result
        assert "rule_score" in result
        assert "triggered_rules" in result
        assert "top_positive_features" in result
        assert "top_negative_features" in result
        assert result["risk_level"] in ("LOW", "MEDIUM", "HIGH")
        assert result["decision"] in ("ALLOW", "REVIEW", "BLOCK")


class TestIEEERiskAPI:
    """API endpoint tests for IEEE risk assessment."""

    def test_assess_endpoint_returns_200(self):
        """POST /api/v1/risk/assess should return 200."""
        response = client.post(
            "/api/v1/risk/assess",
            json={
                "TransactionAmt": 150.0,
                "TransactionDT": 86400 * 3,
                "ProductCD": "C",
                "card1": 100.0,
                "card2": 200.0,
                "card3": 300.0,
                "card4": "visa",
                "P_emaildomain": "gmail.com",
                "R_emaildomain": "gmail.com",
            },
            headers=get_auth_headers(),
        )
        assert response.status_code == 200

    def test_assess_endpoint_returns_valid_response(self):
        """Response should have valid structure."""
        response = client.post(
            "/api/v1/risk/assess",
            json={
                "TransactionAmt": 150.0,
                "TransactionDT": 86400 * 3,
                "ProductCD": "C",
                "card1": 100.0,
                "card2": 200.0,
            },
            headers=get_auth_headers(),
        )
        assert response.status_code == 200
        data = response.json()
        assert "risk_score" in data
        assert "risk_level" in data
        assert data["risk_level"] in ("LOW", "MEDIUM", "HIGH")

    def test_health_endpoint_returns_200(self):
        """GET /api/v1/risk/health should return 200 or 503."""
        response = client.get("/api/v1/risk/health")
        assert response.status_code in (200, 503)

    def test_assess_with_minimal_data(self):
        """Should handle minimal transaction data."""
        response = client.post(
            "/api/v1/risk/assess",
            json={
                "TransactionAmt": 50.0,
                "TransactionDT": 86400,
            },
            headers=get_auth_headers(),
        )
        assert response.status_code == 200
        data = response.json()
        assert "risk_score" in data
        assert data["risk_score"] >= 0
