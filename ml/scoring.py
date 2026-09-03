import logging
from typing import Optional, List, Tuple
from dataclasses import dataclass

import numpy as np

from .models import get_model, BaseModel, ModelRegistry
from . import constants as C

logger = logging.getLogger(__name__)


@dataclass
class MLResult:
    fraud_probability: float
    risk_score: int
    risk_level: str
    decision: str
    model_version: str


def calculate_ml_risk_score(fraud_probability: float) -> int:
    score = int(fraud_probability * C.RISK_SCORE_MULTIPLIER)
    return max(0, min(100, score))


def get_risk_level_from_score(score: int) -> str:
    if score >= C.HIGH_THRESHOLD * 100:
        return "HIGH"
    if score >= C.MEDIUM_THRESHOLD * 100:
        return "MEDIUM"
    return "LOW"


def get_decision_from_level(risk_level: str) -> str:
    if risk_level == "HIGH":
        return "BLOCK"
    if risk_level == "MEDIUM":
        return "REVIEW"
    return "ALLOW"


def predict_fraud_probability(
    amount: float,
    account_age_days: Optional[int],
    previous_transaction_amount: Optional[float],
    transaction_frequency: Optional[int],
    failed_attempts: Optional[int],
    device_change: Optional[bool],
    location_change: Optional[bool],
    merchant_risk: Optional[float],
    velocity: Optional[int],
) -> Tuple[float, str]:
    from .features import extract_features_from_transaction

    features = extract_features_from_transaction(
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

    model = get_model()
    version = model.get_version() if hasattr(model, "get_version") else "unknown"

    feature_vector = np.array([[features.get(name, 0.0) for name in C.FEATURE_NAMES]])

    try:
        fraud_prob = float(model.predict_proba(feature_vector)[0])
    except Exception as e:
        logger.warning(f"ML model inference failed: {e}, using default probability")
        fraud_prob = 0.0

    fraud_prob = max(0.0, min(1.0, fraud_prob))
    return fraud_prob, version


def analyze_with_ml(
    amount: float,
    account_age_days: Optional[int],
    previous_transaction_amount: Optional[float],
    transaction_frequency: Optional[int],
    failed_attempts: Optional[int],
    device_change: Optional[bool],
    location_change: Optional[bool],
    merchant_risk: Optional[float],
    velocity: Optional[int],
) -> MLResult:
    fraud_prob, model_version = predict_fraud_probability(
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

    risk_score = calculate_ml_risk_score(fraud_prob)
    risk_level = get_risk_level_from_score(risk_score)
    decision = get_decision_from_level(risk_level)

    return MLResult(
        fraud_probability=fraud_prob,
        risk_score=risk_score,
        risk_level=risk_level,
        decision=decision,
        model_version=model_version,
    )
