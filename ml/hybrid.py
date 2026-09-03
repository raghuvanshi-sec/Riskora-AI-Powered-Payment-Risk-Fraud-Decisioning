from typing import Optional, List
from dataclasses import dataclass

from app.risk.engine import RulesRiskEngine, TransactionSignals, RiskResult as RulesRiskResult
from app.risk import constants as risk_constants
from .scoring import analyze_with_ml, MLResult
from . import constants as ml_constants


@dataclass
class HybridRiskResult:
    rules_score: int
    rules_level: str
    rules_decision: str
    ml_score: int
    ml_level: str
    ml_decision: str
    ml_probability: float
    final_score: int
    final_level: str
    final_decision: str
    model_version: str
    rules_engine_version: str = "rules-v1"


def compute_hybrid_score(rules_score: int, ml_score: int, rules_weight: float = 0.4, ml_weight: float = 0.6) -> int:
    weighted = (rules_score * rules_weight) + (ml_score * ml_weight)
    return max(0, min(100, int(weighted)))


class HybridRiskEngine:
    def __init__(self, rules_weight: float = 0.4, ml_weight: float = 0.6):
        self.rules_engine = RulesRiskEngine()
        self.rules_weight = rules_weight
        self.ml_weight = ml_weight

    def analyze(
        self,
        amount: float,
        currency: str,
        previous_transaction_amount: Optional[float],
        transaction_frequency: Optional[int],
        failed_attempts: Optional[int],
        device_change: Optional[bool],
        location_change: Optional[bool],
        merchant_risk: Optional[float],
        velocity: Optional[int],
        account_age_days: Optional[int],
        device_id: Optional[str],
        location: Optional[str],
    ) -> HybridRiskResult:
        signals = TransactionSignals(
            amount=amount,
            currency=currency,
            previous_transaction_amount=previous_transaction_amount,
            transaction_frequency=transaction_frequency,
            failed_attempts=failed_attempts,
            device_change=device_change,
            location_change=location_change,
            merchant_risk=merchant_risk,
            velocity=velocity,
            account_age_days=account_age_days,
            device_id=device_id,
            location=location,
        )

        rules_result: RulesRiskResult = self.rules_engine.analyze(signals)

        ml_result: MLResult = analyze_with_ml(
            amount=amount,
            account_age_days=account_age_days,
            previous_transaction_amount=previous_transaction_amount,
            transaction_frequency=transaction_frequency,
            failed_attempts=failed_attempts,
            device_change=device_change,
            location_change=location_change,
            merchant_risk=merchant_risk,
            velocity=velocity,
        )

        final_score = compute_hybrid_score(
            rules_result.risk_score,
            ml_result.risk_score,
            self.rules_weight,
            self.ml_weight,
        )

        if final_score >= risk_constants.HIGH_THRESHOLD:
            final_level = risk_constants.RISK_LEVEL_HIGH
        elif final_score >= risk_constants.LOW_THRESHOLD:
            final_level = risk_constants.RISK_LEVEL_MEDIUM
        else:
            final_level = risk_constants.RISK_LEVEL_LOW

        if final_level == risk_constants.RISK_LEVEL_HIGH:
            final_decision = risk_constants.DECISION_HIGH
        elif final_level == risk_constants.RISK_LEVEL_MEDIUM:
            final_decision = risk_constants.DECISION_MEDIUM
        else:
            final_decision = risk_constants.DECISION_LOW

        return HybridRiskResult(
            rules_score=rules_result.risk_score,
            rules_level=rules_result.risk_level,
            rules_decision=rules_result.decision,
            ml_score=ml_result.risk_score,
            ml_level=ml_result.risk_level,
            ml_decision=ml_result.decision,
            ml_probability=ml_result.fraud_probability,
            final_score=final_score,
            final_level=final_level,
            final_decision=final_decision,
            model_version=ml_result.model_version,
            rules_engine_version="rules-v1",
        )


def get_default_hybrid_engine() -> HybridRiskEngine:
    return HybridRiskEngine()
