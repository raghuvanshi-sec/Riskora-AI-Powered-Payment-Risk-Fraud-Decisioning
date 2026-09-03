import logging
from dataclasses import dataclass
from typing import Optional, List

logger = logging.getLogger(__name__)

try:
    import shap
    import numpy as np
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    shap = None
    np = None


FEATURE_NAMES = [
    "transaction_amount", "account_age_days", "previous_transaction_amount",
    "transaction_frequency", "failed_attempts", "device_change",
    "location_change", "merchant_risk", "velocity_1h", "velocity_24h"
]


@dataclass
class FeatureContribution:
    feature_name: str
    feature_value: float
    contribution: float
    direction: str


@dataclass
class SHAPValues:
    base_value: float
    feature_values: dict
    shap_values: dict
    feature_contributions: List[FeatureContribution]
    model_version: str
    available: bool = False


def _extract_features(**kwargs) -> dict:
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


def explain_transaction(model=None, model_version: str = "unknown", **kwargs) -> SHAPValues:
    if not SHAP_AVAILABLE or model is None:
        features = _extract_features(**kwargs)
        contributions = []
        for fname in FEATURE_NAMES:
            fval = features.get(fname, 0.0)
            contrib = (fval - 0.5) * 0.2
            contributions.append(FeatureContribution(
                feature_name=fname,
                feature_value=fval,
                contribution=round(contrib, 4),
                direction="positive" if contrib > 0 else "negative"
            ))
        
        contributions.sort(key=lambda x: abs(x.contribution), reverse=True)
        
        return SHAPValues(
            base_value=0.5,
            feature_values=features,
            shap_values={},
            feature_contributions=contributions[:8],
            model_version=model_version if model_version else "none",
            available=False
        )
    
    try:
        features = _extract_features(**kwargs)
        feature_vector = [[features.get(fn, 0.0) for fn in FEATURE_NAMES]]
        
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(feature_vector)
        
        if isinstance(shap_values, list):
            sv = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
        else:
            sv = shap_values[0]
        
        contributions = []
        for i, fname in enumerate(FEATURE_NAMES):
            contributions.append(FeatureContribution(
                feature_name=fname,
                feature_value=features.get(fname, 0.0),
                contribution=round(float(sv[i]), 4),
                direction="positive" if sv[i] > 0 else "negative"
            ))
        
        contributions.sort(key=lambda x: abs(x.contribution), reverse=True)
        
        logger.info(f"[SHAP] Generated explanation for {model_version}")
        
        return SHAPValues(
            base_value=float(explainer.expected_value[1]) if isinstance(explainer.expected_value, list) else float(explainer.expected_value),
            feature_values=features,
            shap_values={fname: float(sv[i]) for i, fname in enumerate(FEATURE_NAMES)},
            feature_contributions=contributions[:10],
            model_version=model_version,
            available=True
        )
        
    except Exception as e:
        logger.error(f"SHAP explanation error: {e}")
        features = _extract_features(**kwargs)
        contributions = []
        for fname in FEATURE_NAMES:
            fval = features.get(fname, 0.0)
            contrib = (fval - 0.5) * 0.15
            contributions.append(FeatureContribution(
                feature_name=fname,
                feature_value=fval,
                contribution=round(contrib, 4),
                direction="positive" if contrib > 0 else "negative"
            ))
        
        contributions.sort(key=lambda x: abs(x.contribution), reverse=True)
        
        return SHAPValues(
            base_value=0.0,
            feature_values=features,
            shap_values={},
            feature_contributions=contributions[:8],
            model_version=model_version if model_version else "error",
            available=False
        )
