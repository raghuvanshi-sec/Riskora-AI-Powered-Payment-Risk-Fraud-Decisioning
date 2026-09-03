import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
import numpy as np

from . import constants as C

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ML_ARTIFACTS_DIR = PROJECT_ROOT / "ml" / "artifacts"
ML_REPORTS_DIR = PROJECT_ROOT / "ml" / "reports"

_SHAP_AVAILABLE = False
_Explainer = None

try:
    import shap
    _SHAP_AVAILABLE = True
    _Explainer = shap.Explainer
except ImportError:
    logger.warning("SHAP not available. Install with: pip install shap")


@dataclass
class SHAPValues:
    base_value: float
    feature_values: Dict[str, float]
    shap_values: Dict[str, float]
    feature_contributions: List[Dict]
    model_version: str
    available: bool = True


@dataclass
class FeatureContribution:
    feature_name: str
    feature_value: float
    contribution: float
    direction: str


def get_shap_available() -> bool:
    return _SHAP_AVAILABLE


def _get_feature_contribution_direction(contribution: float) -> str:
    if contribution > 0:
        return "increases"
    elif contribution < 0:
        return "decreases"
    return "neutral"


def explain_with_shap(
    model,
    feature_vector: np.ndarray,
    feature_names: List[str],
    model_version: str,
) -> SHAPValues:
    if not _SHAP_AVAILABLE:
        return SHAPValues(
            base_value=0.0,
            feature_values={},
            shap_values={},
            feature_contributions=[],
            model_version=model_version,
            available=False,
        )

    try:
        explainer = shap.Explainer(model.predict_proba, feature_vector)
        shap_values = explainer(feature_vector)

        shap_vals = shap_values.values[0] if len(shap_values.shape) > 1 else shap_values.values
        base_val = shap_values.base_values[0] if hasattr(shap_values, "base_values") else 0.0

        feature_values = {name: float(feature_vector[0][i]) for i, name in enumerate(feature_names)}
        shap_dict = {name: float(shap_vals[i]) for i, name in enumerate(feature_names)}

        contributions = []
        for i, name in enumerate(feature_names):
            contrib = float(shap_vals[i])
            contributions.append(FeatureContribution(
                feature_name=name,
                feature_value=float(feature_vector[0][i]),
                contribution=contrib,
                direction=_get_feature_contribution_direction(contrib),
            ))

        contributions.sort(key=lambda x: abs(x.contribution), reverse=True)

        return SHAPValues(
            base_value=float(base_val),
            feature_values=feature_values,
            shap_values=shap_dict,
            feature_contributions=contributions,
            model_version=model_version,
            available=True,
        )
    except Exception as e:
        logger.warning(f"SHAP explanation failed: {e}")
        return SHAPValues(
            base_value=0.0,
            feature_values={},
            shap_values={},
            feature_contributions=[],
            model_version=model_version,
            available=False,
        )


def explain_mock_model(
    feature_vector: np.ndarray,
    feature_names: List[str],
    model_version: str,
) -> SHAPValues:
    contributions = []
    for i, name in enumerate(feature_names):
        val = float(feature_vector[0][i])
        contrib = val * 0.01 if val > 0 else 0.0
        contributions.append(FeatureContribution(
            feature_name=name,
            feature_value=val,
            contribution=contrib,
            direction=_get_feature_contribution_direction(contrib),
        ))

    contributions.sort(key=lambda x: abs(x.contribution), reverse=True)

    return SHAPValues(
        base_value=0.0,
        feature_values={name: float(feature_vector[0][i]) for i, name in enumerate(feature_names)},
        shap_values={name: 0.0 for name in feature_names},
        feature_contributions=contributions,
        model_version=model_version,
        available=False,
    )


def explain_transaction(
    model,
    amount: float,
    account_age_days: Optional[int],
    previous_transaction_amount: Optional[float],
    transaction_frequency: Optional[int],
    failed_attempts: Optional[int],
    device_change: Optional[bool],
    location_change: Optional[bool],
    merchant_risk: Optional[float],
    velocity: Optional[int],
    model_version: str = "unknown",
) -> SHAPValues:
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

    feature_vector = np.array([[features.get(name, 0.0) for name in C.FEATURE_NAMES]])

    if hasattr(model, "predict_proba"):
        return explain_with_shap(model, feature_vector, C.FEATURE_NAMES, model_version)
    else:
        return explain_mock_model(feature_vector, C.FEATURE_NAMES, model_version)


class RiskoraSHAPExplainer:
    """SHAP explainer for the IEEE-CIS XGBoost model."""

    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.model_name = None
        self.model_version = None
        self.feature_names: List[str] = []
        self.explainer = None

    def load_model(self, model_path: Optional[Path] = None) -> None:
        """Load the XGBoost model from artifact."""
        import joblib

        if model_path is None:
            model_path = ML_ARTIFACTS_DIR / "risk_model_v1.joblib"

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found at {model_path}")

        model_artifact = joblib.load(model_path)
        self.model = model_artifact["model"]
        self.model_name = model_artifact.get("model_name", "unknown")
        self.model_version = model_artifact.get("model_version", "unknown")

        logger.info("Loaded model: %s (%s)", self.model_name, self.model_version)

    def load_preprocessor(self, preprocessor_path: Optional[Path] = None) -> None:
        """Load the fitted preprocessor."""
        import joblib

        if preprocessor_path is None:
            preprocessor_path = ML_ARTIFACTS_DIR / "preprocessor_ieee_cis_v1.joblib"

        if not preprocessor_path.exists():
            raise FileNotFoundError(f"Preprocessor not found at {preprocessor_path}")

        self.preprocessor = joblib.load(preprocessor_path)
        logger.info("Loaded preprocessor from: %s", preprocessor_path)

    def get_feature_names(self) -> List[str]:
        """Get transformed feature names from preprocessor."""
        if self.preprocessor is None:
            return []

        try:
            self.feature_names = self.preprocessor.get_feature_names_out().tolist()
        except Exception as e:
            logger.warning("Could not get feature names from preprocessor: %s", e)
            self.feature_names = []

        return self.feature_names

    def build_explainer(self) -> None:
        """Build the SHAP TreeExplainer."""
        if not _SHAP_AVAILABLE:
            raise RuntimeError("SHAP is not available")

        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        self.explainer = shap.TreeExplainer(self.model)
        logger.info("Built SHAP TreeExplainer")

    def transform_features(self, X: pd.DataFrame) -> np.ndarray:
        """Transform features using the preprocessor."""
        if self.preprocessor is None:
            raise RuntimeError("Preprocessor not loaded. Call load_preprocessor() first.")

        return self.preprocessor.transform(X)

    @staticmethod
    def map_transformed_name(original_name: str) -> str:
        """Map transformed feature name back to original."""
        if original_name.startswith("num__"):
            return original_name[5:]
        elif original_name.startswith("cat__"):
            parts = original_name[5:].split("_", 1)
            if len(parts) == 2 and parts[1].isdigit():
                return parts[0]
            return original_name[5:]
        return original_name

    def explain(self, X_transformed: np.ndarray) -> Dict[str, Any]:
        """Generate SHAP explanation for transformed features."""
        if self.explainer is None:
            raise RuntimeError("Explainer not built. Call build_explainer() first.")

        shap_output = self.explainer(X_transformed)

        shap_values = shap_output.values[0]
        base_value = shap_output.base_values[0]

        shap_dict = {}
        for i, name in enumerate(self.feature_names):
            shap_dict[name] = float(shap_values[i])

        return {
            "shap_values": shap_dict,
            "base_value": float(base_value),
            "expected_value": float(base_value),
        }

    def explain_single(self, X_df: pd.DataFrame) -> Dict[str, Any]:
        """Explain a single transaction DataFrame."""
        X_transformed = self.transform_features(X_df)
        result = self.explain(X_transformed)

        model_proba = float(self.model.predict_proba(X_transformed)[0][1])

        return {
            "prediction_probability": model_proba,
            "prediction_class": int(self.model.predict(X_transformed)[0]),
            "base_value": result["base_value"],
            "shap_values": result["shap_values"],
            "feature_names": self.feature_names,
        }

    def get_top_features(
        self,
        shap_values: Dict[str, float],
        top_n: int = 10
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Get top positive and negative SHAP contributors."""
        sorted_features = sorted(
            shap_values.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )

        positive = []
        negative = []

        for name, value in sorted_features:
            if len(positive) >= top_n and len(negative) >= top_n:
                break

            contributor = {
                "transformed_name": name,
                "original_name": self.map_transformed_name(name),
                "shap_value": value,
                "direction": "increases_risk" if value > 0 else "decreases_risk",
            }

            if value > 0 and len(positive) < top_n:
                positive.append(contributor)
            elif value < 0 and len(negative) < top_n:
                negative.append(contributor)

        return positive, negative

    def generate_explanation_text(self, contributor: Dict[str, Any]) -> str:
        """Generate human-readable explanation for a SHAP contributor."""
        original_name = contributor["original_name"]
        shap_value = contributor["shap_value"]
        direction = contributor["direction"]

        if direction == "increases_risk":
            return f"{original_name} increased the model's predicted fraud risk (SHAP: {shap_value:.4f})"
        else:
            return f"{original_name} decreased the model's predicted fraud risk (SHAP: {shap_value:.4f})"

    def validate_reconstruction(
        self,
        base_value: float,
        shap_values: Dict[str, float],
        model_proba: float,
        tolerance: float = 0.01
    ) -> Tuple[bool, float]:
        """Validate SHAP reconstruction."""
        shap_sum = sum(shap_values.values())
        reconstruction = base_value + shap_sum

        expected_proba = 1 / (1 + math.exp(-reconstruction))
        error = abs(expected_proba - model_proba)
        passed = error < tolerance

        return passed, error
