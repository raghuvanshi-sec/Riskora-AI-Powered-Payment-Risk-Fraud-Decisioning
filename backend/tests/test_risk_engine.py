"""Tests for the rule-based risk engine.

Covers:
- Rule evaluation (each rule independently)
- Score calculation and clamping (0-100)
- Risk level mapping (LOW/MEDIUM/HIGH)
- Decision mapping (ALLOW/REVIEW/BLOCK)
- Multiple rules triggering simultaneously
- Explanation generation
- End-to-end risk analysis
"""

import pytest
from app.risk.engine import RulesRiskEngine, RiskResult
from app.risk.feature_extractor import TransactionSignals, extract_signals
from app.risk import scoring, constants as C
from app.risk.rules import (
    UnusualAmountRule, HighAmountRule, NewDeviceRule,
    LocationChangeRule, HighVelocityRule, FailedAttemptsRule,
    MerchantRiskRule, NewAccountRule, get_all_rules
)


def signals(**overrides):
    defaults = dict(
        amount=1000.0,
        currency="INR",
        previous_transaction_amount=500.0,
        transaction_frequency=5,
        failed_attempts=0,
        device_change=False,
        location_change=False,
        merchant_risk=20.0,
        velocity=1,
        account_age_days=365,
        device_id="iPhone-14-Pro",
        location="Mumbai",
    )
    defaults.update(overrides)
    return TransactionSignals(**defaults)


def analyze(**overrides):
    sigs = signals(**overrides)
    engine = RulesRiskEngine()
    return engine.analyze(sigs)


class TestRules:
    def test_unusual_amount_rule_triggers(self):
        rule = UnusualAmountRule()
        # amount = 5000, prev = 500 -> 10x -> should trigger
        factor = rule.evaluate(signals(amount=5000, previous_transaction_amount=500))
        assert factor is not None
        assert factor.code == "UNUSUAL_AMOUNT"
        assert factor.contribution == C.WEIGHT_UNUSUAL_AMOUNT

    def test_unusual_amount_rule_no_trigger(self):
        rule = UnusualAmountRule()
        # amount = 1000, prev = 500 -> 2x -> should NOT trigger (threshold is 5x)
        factor = rule.evaluate(signals(amount=1000, previous_transaction_amount=500))
        assert factor is None

    def test_unusual_amount_rule_zero_prev(self):
        rule = UnusualAmountRule()
        # previous = 0 should not trigger division error
        factor = rule.evaluate(signals(amount=5000, previous_transaction_amount=0))
        assert factor is None

    def test_unusual_amount_rule_null_prev(self):
        rule = UnusualAmountRule()
        factor = rule.evaluate(signals(previous_transaction_amount=None))
        assert factor is None

    def test_high_amount_rule_triggers(self):
        rule = HighAmountRule()
        # > 75000 triggers
        factor = rule.evaluate(signals(amount=100000))
        assert factor is not None
        assert factor.code == "HIGH_AMOUNT"

    def test_high_amount_rule_no_trigger(self):
        rule = HighAmountRule()
        # < 75000 does not trigger
        factor = rule.evaluate(signals(amount=50000))
        assert factor is None

    def test_new_device_rule_triggers(self):
        rule = NewDeviceRule()
        factor = rule.evaluate(signals(device_change=True))
        assert factor is not None
        assert factor.code == "NEW_DEVICE"

    def test_new_device_rule_no_trigger(self):
        rule = NewDeviceRule()
        factor = rule.evaluate(signals(device_change=False))
        assert factor is None

    def test_location_change_rule_triggers(self):
        rule = LocationChangeRule()
        factor = rule.evaluate(signals(location_change=True))
        assert factor is not None
        assert factor.code == "LOCATION_CHANGE"

    def test_location_change_rule_no_trigger(self):
        rule = LocationChangeRule()
        factor = rule.evaluate(signals(location_change=False))
        assert factor is None

    def test_high_velocity_rule_triggers(self):
        rule = HighVelocityRule()
        # velocity > 6 triggers
        factor = rule.evaluate(signals(velocity=10))
        assert factor is not None
        assert factor.code == "HIGH_VELOCITY"

    def test_high_velocity_rule_no_trigger(self):
        rule = HighVelocityRule()
        # velocity <= 6 does not trigger
        factor = rule.evaluate(signals(velocity=5))
        assert factor is None

    def test_high_velocity_rule_null(self):
        rule = HighVelocityRule()
        factor = rule.evaluate(signals(velocity=None))
        assert factor is None

    def test_failed_attempts_rule_triggers(self):
        rule = FailedAttemptsRule()
        # >= 4 triggers
        factor = rule.evaluate(signals(failed_attempts=5))
        assert factor is not None
        assert factor.code == "MULTIPLE_FAILED_ATTEMPTS"

    def test_failed_attempts_rule_no_trigger(self):
        rule = FailedAttemptsRule()
        # < 4 does not trigger
        factor = rule.evaluate(signals(failed_attempts=2))
        assert factor is None

    def test_merchant_risk_rule_triggers(self):
        rule = MerchantRiskRule()
        # merchant_risk > 61 triggers
        factor = rule.evaluate(signals(merchant_risk=75))
        assert factor is not None
        assert factor.code == "HIGH_MERCHANT_RISK"

    def test_merchant_risk_rule_no_trigger(self):
        rule = MerchantRiskRule()
        # merchant_risk <= 61 does not trigger
        factor = rule.evaluate(signals(merchant_risk=50))
        assert factor is None

    def test_merchant_risk_rule_null(self):
        rule = MerchantRiskRule()
        factor = rule.evaluate(signals(merchant_risk=None))
        assert factor is None

    def test_new_account_rule_triggers(self):
        rule = NewAccountRule()
        # < 30 days triggers
        factor = rule.evaluate(signals(account_age_days=15))
        assert factor is not None
        assert factor.code == "NEW_ACCOUNT"

    def test_new_account_rule_no_trigger(self):
        rule = NewAccountRule()
        # >= 30 days does not trigger
        factor = rule.evaluate(signals(account_age_days=60))
        assert factor is None

    def test_new_account_rule_null(self):
        rule = NewAccountRule()
        factor = rule.evaluate(signals(account_age_days=None))
        assert factor is None

    def test_all_rules_exist(self):
        rules = get_all_rules()
        rule_ids = {r.rule_id for r in rules}
        expected = {
            "UNUSUAL_AMOUNT", "HIGH_AMOUNT", "NEW_DEVICE",
            "LOCATION_CHANGE", "HIGH_VELOCITY", "MULTIPLE_FAILED_ATTEMPTS",
            "HIGH_MERCHANT_RISK", "NEW_ACCOUNT"
        }
        assert rule_ids == expected


class TestScoring:
    def test_score_zero_no_factors(self):
        score = scoring.calculate_score([])
        assert score == 0

    def test_score_single_factor(self):
        rule = UnusualAmountRule()
        # amount = 5000, prev = 500 -> triggers
        sigs = signals(amount=5000, previous_transaction_amount=500)
        factor = rule.evaluate(sigs)
        score = scoring.calculate_score([factor])
        assert score == C.WEIGHT_UNUSUAL_AMOUNT

    def test_score_multiple_factors(self):
        factors = []
        for rule in get_all_rules():
            f = rule.evaluate(signals(
                amount=200000,
                previous_transaction_amount=500,
                device_change=True,
                location_change=True,
                velocity=10,
                failed_attempts=5,
                merchant_risk=80,
                account_age_days=10,
            ))
            if f:
                factors.append(f)
        score = scoring.calculate_score(factors)
        assert score <= C.MAX_SCORE
        assert score >= 0

    def test_score_capped_at_100(self):
        # Add many high-contributing factors
        factors = []
        for _ in range(10):
            for rule in get_all_rules():
                f = rule.evaluate(signals(
                    amount=500000,
                    previous_transaction_amount=100,
                    device_change=True,
                    location_change=True,
                    velocity=20,
                    failed_attempts=10,
                    merchant_risk=100,
                    account_age_days=5,
                ))
                if f:
                    factors.append(f)
        score = scoring.calculate_score(factors)
        assert score == C.MAX_SCORE

    def test_score_never_negative(self):
        # Empty list should give 0
        score = scoring.calculate_score([])
        assert score >= 0


class TestRiskLevel:
    def test_low_level(self):
        assert scoring.get_risk_level(0) == C.RISK_LEVEL_LOW
        assert scoring.get_risk_level(15) == C.RISK_LEVEL_LOW
        assert scoring.get_risk_level(29) == C.RISK_LEVEL_LOW

    def test_medium_level(self):
        assert scoring.get_risk_level(30) == C.RISK_LEVEL_MEDIUM
        assert scoring.get_risk_level(50) == C.RISK_LEVEL_MEDIUM
        assert scoring.get_risk_level(69) == C.RISK_LEVEL_MEDIUM

    def test_high_level(self):
        assert scoring.get_risk_level(70) == C.RISK_LEVEL_HIGH
        assert scoring.get_risk_level(85) == C.RISK_LEVEL_HIGH
        assert scoring.get_risk_level(100) == C.RISK_LEVEL_HIGH


class TestDecision:
    def test_low_decision(self):
        assert scoring.get_decision(C.RISK_LEVEL_LOW) == C.DECISION_LOW

    def test_medium_decision(self):
        assert scoring.get_decision(C.RISK_LEVEL_MEDIUM) == C.DECISION_MEDIUM

    def test_high_decision(self):
        assert scoring.get_decision(C.RISK_LEVEL_HIGH) == C.DECISION_HIGH


class TestExplanation:
    def test_explanation_no_factors(self):
        explanation = scoring.generate_explanation([], C.RISK_LEVEL_LOW)
        assert "No risk factors detected" in explanation

    def test_explanation_single_factor(self):
        rule = NewDeviceRule()
        factor = rule.evaluate(signals(device_change=True))
        explanation = scoring.generate_explanation([factor], C.RISK_LEVEL_MEDIUM)
        assert "new device" in explanation.lower()

    def test_explanation_multiple_factors(self):
        factors = []
        for rule in get_all_rules():
            f = rule.evaluate(signals(
                amount=100000,
                previous_transaction_amount=500,
                device_change=True,
            ))
            if f:
                factors.append(f)
        explanation = scoring.generate_explanation(factors, C.RISK_LEVEL_HIGH)
        assert len(explanation) > 0


class TestEndToEnd:
    def test_normal_transaction_low_risk(self):
        result = analyze(
            amount=1000,
            previous_transaction_amount=800,
            device_change=False,
            location_change=False,
            velocity=1,
            failed_attempts=0,
            merchant_risk=10,
            account_age_days=365,
        )
        assert result.risk_score < C.LOW_THRESHOLD
        assert result.risk_level == C.RISK_LEVEL_LOW
        assert result.decision == C.DECISION_LOW

    def test_high_risk_transaction(self):
        result = analyze(
            amount=150000,
            previous_transaction_amount=500,
            device_change=True,
            location_change=True,
            velocity=10,
            failed_attempts=5,
            merchant_risk=85,
            account_age_days=10,
        )
        assert result.risk_score >= C.HIGH_THRESHOLD
        assert result.risk_level == C.RISK_LEVEL_HIGH
        assert result.decision == C.DECISION_HIGH

    def test_medium_risk_transaction(self):
        result = analyze(
            amount=80000,
            previous_transaction_amount=500,
            device_change=True,
            location_change=False,
            velocity=4,
            failed_attempts=0,
            merchant_risk=35,
            account_age_days=60,
        )
        assert C.LOW_THRESHOLD <= result.risk_score < C.HIGH_THRESHOLD
        assert result.risk_level == C.RISK_LEVEL_MEDIUM
        assert result.decision == C.DECISION_MEDIUM

    def test_model_version_is_rules_v1(self):
        result = analyze()
        assert result.model_version == C.RISK_MODEL_VERSION

    def test_risk_factors_returned(self):
        result = analyze(
            amount=200000,
            previous_transaction_amount=500,
            device_change=True,
            velocity=10,
        )
        assert len(result.risk_factors) > 0

    def test_score_within_bounds(self):
        for _ in range(50):
            result = analyze(
                amount=1000 + _ * 1000,
                previous_transaction_amount=500 + _ * 100,
                device_change=_ % 2 == 0,
                location_change=_ % 3 == 0,
                velocity=_ % 7,
                failed_attempts=_ % 5,
                merchant_risk=_ % 100,
                account_age_days=10 + _ * 20,
            )
            assert 0 <= result.risk_score <= C.MAX_SCORE
