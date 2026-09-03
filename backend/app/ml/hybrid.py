import logging
import time
from dataclasses import dataclass
from typing import Optional

from app.ml.models import get_model, ModelRegistry

logger = logging.getLogger(__name__)


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
    inference_time_ms: float = 0.0
    feature_count: int = 0


class HybridRiskEngine:
    def __init__(self):
        self.model = get_model()
        self.artifact = ModelRegistry.get_active()
        self.feature_names = self.artifact.feature_names if self.artifact else []

    def _extract_features(self, **kwargs) -> dict:
        return {
            "transaction_amount": kwargs.get("amount", 0) / 1000.0,
            "account_age_days": kwargs.get("account_age_days", 365) / 365.0,
            "previous_transaction_amount": kwargs.get("previous_transaction_amount", 0) / 1000.0,
            "transaction_frequency": min(kwargs.get("transaction_frequency", 1) / 10.0, 1.0),
            "failed_attempts": min(kwargs.get("failed_attempts", 0) / 5.0, 1.0),
            "device_change": float(kwargs.get("device_change", 0)),
            "location_change": float(kwargs.get("location_change", 0)),
            "merchant_risk": kwargs.get("merchant_risk", 0.5),
            "velocity_1h": min(kwargs.get("velocity", 1) / 10.0, 1.0),
            "velocity_24h": min(kwargs.get("velocity", 1) / 20.0, 1.0),
        }

    def _ml_score_to_risk(self, prob: float) -> int:
        return int(min(100, max(0, prob * 100)))

    def _score_to_level(self, score: int) -> str:
        if score >= 70:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        return "LOW"

    def _score_to_decision(self, score: int) -> str:
        if score >= 70:
            return "BLOCK"
        elif score >= 40:
            return "REVIEW"
        return "ALLOW"

    def analyze(self, **kwargs) -> HybridRiskResult:
        start_time = time.perf_counter()
        
        features = self._extract_features(**kwargs)
        feature_vector = [features.get(fn, 0.0) for fn in self.feature_names]
        
        ml_score = 0
        ml_probability = 0.0
        ml_level = "LOW"
        ml_decision = "ALLOW"
        model_version = "none"
        
        if self.model is not None:
            try:
                import numpy as np
                X = np.array([feature_vector])
                proba = self.model.predict_proba(X)[0]
                ml_probability = float(proba[1])
                ml_score = self._ml_score_to_risk(ml_probability)
                ml_level = self._score_to_level(ml_score)
                ml_decision = self._score_to_decision(ml_score)
                model_version = self.artifact.version if self.artifact else "unknown"
            except Exception as e:
                logger.error(f"ML inference error: {e}")
                ml_probability = 0.1
                ml_score = 10
                ml_level = "LOW"
                ml_decision = "ALLOW"
                model_version = "error"
        
        base_rules_score = int(
            features["failed_attempts"] * 20 +
            features["device_change"] * 25 +
            features["location_change"] * 15 +
            features["merchant_risk"] * 30 +
            features["velocity_1h"] * 10
        )
        rules_score = min(100, base_rules_score)
        rules_level = self._score_to_level(rules_score)
        rules_decision = self._score_to_decision(rules_score)
        
        if ml_score > 0:
            final_score = int(rules_score * 0.4 + ml_score * 0.6)
        else:
            final_score = rules_score
        
        final_level = self._score_to_level(final_score)
        final_decision = self._score_to_decision(final_score)
        
        inference_time = (time.perf_counter() - start_time) * 1000
        
        logger.info(
            f"[ML INFERENCE] Transaction features={len(feature_vector)} "
            f"Model={model_version} Fraud Prob={ml_probability:.4f} "
            f"Inference Time={inference_time:.2f}ms"
        )
        
        return HybridRiskResult(
            rules_score=rules_score,
            rules_level=rules_level,
            rules_decision=rules_decision,
            ml_score=ml_score,
            ml_level=ml_level,
            ml_decision=ml_decision,
            ml_probability=ml_probability,
            final_score=final_score,
            final_level=final_level,
            final_decision=final_decision,
            model_version=model_version,
            rules_engine_version="rules-v1",
            inference_time_ms=round(inference_time, 2),
            feature_count=len(self.feature_names),
        )
