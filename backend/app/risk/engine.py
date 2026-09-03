from dataclasses import dataclass
from typing import List, Optional
from app.risk.feature_extractor import TransactionSignals, extract_signals
from app.risk.rules import get_all_rules, RiskFactor
from app.risk import scoring, constants as C


@dataclass
class RiskResult:
    risk_score: int
    risk_level: str
    decision: str
    risk_factors: List[RiskFactor]
    explanation: str
    model_version: str


class RiskEngine:
    def analyze(self, signals: TransactionSignals) -> RiskResult:
        raise NotImplementedError


class RulesRiskEngine(RiskEngine):
    def analyze(self, signals: TransactionSignals) -> RiskResult:
        triggered_factors: List[RiskFactor] = []
        for rule in get_all_rules():
            factor = rule.evaluate(signals)
            if factor is not None:
                triggered_factors.append(factor)

        score = scoring.calculate_score(triggered_factors)
        level = scoring.get_risk_level(score)
        decision = scoring.get_decision(level)
        explanation = scoring.generate_explanation(triggered_factors, level)

        return RiskResult(
            risk_score=score,
            risk_level=level,
            decision=decision,
            risk_factors=triggered_factors,
            explanation=explanation,
            model_version=C.RISK_MODEL_VERSION,
        )


def analyze_transaction_signals(
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
) -> RiskResult:
    signals = extract_signals(
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
    engine = RulesRiskEngine()
    return engine.analyze(signals)
