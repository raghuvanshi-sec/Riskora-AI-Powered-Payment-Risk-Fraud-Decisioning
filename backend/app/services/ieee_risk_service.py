"""
IEEE-CIS Risk Inference Service
==============================

Production risk inference service using the trained XGBoost model
and IEEE-CIS feature engineering pipeline.

Loads model/preprocessor once at startup for efficiency.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

ML_ARTIFACTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "ml" / "artifacts"
MODEL_PATH = ML_ARTIFACTS_DIR / "risk_model_v1.joblib"
PREPROCESSOR_PATH = ML_ARTIFACTS_DIR / "preprocessor_ieee_cis_v1.joblib"

ML_WEIGHT = 0.70
RULE_WEIGHT = 0.30
LOW_THRESHOLD = 30
HIGH_THRESHOLD = 70
AMOUNT_HIGH_THRESHOLD = 300.0
AMOUNT_LOG_HIGH_THRESHOLD = 5.7
TRANSACTION_HOUR_SUSPICIOUS = 3
DEVICE_TYPE_THRESHOLD = 0.5


class IEEE_CIS_RuleEngine:
    """Deterministic rule engine for IEEE-CIS transactions."""

    def evaluate(self, transaction: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """Evaluate all applicable rules."""
        rules = []

        amount = transaction.get("amount", 0)
        amount_log = transaction.get("amount_log", 0)
        hour = transaction.get("transaction_hour", None)
        p_email = transaction.get("P_emaildomain", None)
        r_email = transaction.get("R_emaildomain", None)
        device_type_present = transaction.get("device_type_present", 0)
        device_info_present = transaction.get("device_info_present", 0)
        card2 = transaction.get("card2", None)
        card3 = transaction.get("card3", None)
        product = transaction.get("product_code", None)

        rule_score = 0

        if amount > AMOUNT_HIGH_THRESHOLD:
            rules.append({
                "rule_id": "RULE_HIGH_AMOUNT",
                "name": "High Transaction Amount",
                "severity": "HIGH",
                "score_contribution": 20,
                "triggered": True,
                "reason": f"Transaction amount ${amount:.2f} exceeds threshold ${AMOUNT_HIGH_THRESHOLD}"
            })
            rule_score += 20
        elif amount_log > AMOUNT_LOG_HIGH_THRESHOLD:
            rules.append({
                "rule_id": "RULE_HIGH_AMOUNT",
                "name": "High Transaction Amount (log)",
                "severity": "MEDIUM",
                "score_contribution": 15,
                "triggered": True,
                "reason": f"Transaction amount log {amount_log:.2f} exceeds threshold"
            })
            rule_score += 15
        else:
            rules.append({
                "rule_id": "RULE_HIGH_AMOUNT",
                "name": "High Transaction Amount",
                "severity": "LOW",
                "score_contribution": 0,
                "triggered": False,
                "reason": "Amount within normal range"
            })

        if hour is not None and hour < TRANSACTION_HOUR_SUSPICIOUS:
            rules.append({
                "rule_id": "RULE_UNUSUAL_HOUR",
                "name": "Unusual Transaction Hour",
                "severity": "MEDIUM",
                "score_contribution": 10,
                "triggered": True,
                "reason": f"Transaction at hour {hour:.2f} is unusual"
            })
            rule_score += 10
        else:
            rules.append({
                "rule_id": "RULE_UNUSUAL_HOUR",
                "name": "Unusual Transaction Hour",
                "severity": "LOW",
                "score_contribution": 0,
                "triggered": False,
                "reason": "Normal transaction hour"
            })

        p_present = p_email and str(p_email).strip() not in ("", "missing", "nan")
        r_present = r_email and str(r_email).strip() not in ("", "missing", "nan")

        if not p_present:
            rules.append({
                "rule_id": "RULE_MISSING_BILLING_EMAIL",
                "name": "Missing Billing Email",
                "severity": "LOW",
                "score_contribution": 5,
                "triggered": True,
                "reason": "Billing email is missing or invalid"
            })
            rule_score += 5
        else:
            rules.append({
                "rule_id": "RULE_MISSING_BILLING_EMAIL",
                "name": "Missing Billing Email",
                "severity": "LOW",
                "score_contribution": 0,
                "triggered": False,
                "reason": "Billing email present"
            })

        if p_present and r_present and p_email != r_email:
            rules.append({
                "rule_id": "RULE_EMAIL_MISMATCH",
                "name": "Email Domain Mismatch",
                "severity": "MEDIUM",
                "score_contribution": 15,
                "triggered": True,
                "reason": f"Billing email ({p_email}) differs from recipient ({r_email})"
            })
            rule_score += 15
        else:
            rules.append({
                "rule_id": "RULE_EMAIL_MISMATCH",
                "name": "Email Domain Mismatch",
                "severity": "LOW",
                "score_contribution": 0,
                "triggered": False,
                "reason": "Email domains match or N/A"
            })

        if device_type_present is not None and device_type_present < DEVICE_TYPE_THRESHOLD:
            rules.append({
                "rule_id": "RULE_MISSING_DEVICE",
                "name": "Missing Device Information",
                "severity": "MEDIUM",
                "score_contribution": 10,
                "triggered": True,
                "reason": "Device type is missing"
            })
            rule_score += 10
        else:
            rules.append({
                "rule_id": "RULE_MISSING_DEVICE",
                "name": "Missing Device Information",
                "severity": "LOW",
                "score_contribution": 0,
                "triggered": False,
                "reason": "Device information present"
            })

        missing_card = 0
        if card2 is None or (isinstance(card2, float) and np.isnan(card2)):
            missing_card += 1
        if card3 is None or (isinstance(card3, float) and np.isnan(card3)):
            missing_card += 1

        if missing_card >= 2:
            rules.append({
                "rule_id": "RULE_MISSING_CARD_INFO",
                "name": "Missing Card Information",
                "severity": "MEDIUM",
                "score_contribution": 10,
                "triggered": True,
                "reason": f"{missing_card} card fields missing"
            })
            rule_score += 10
        else:
            rules.append({
                "rule_id": "RULE_MISSING_CARD_INFO",
                "name": "Missing Card Information",
                "severity": "LOW",
                "score_contribution": 0,
                "triggered": False,
                "reason": "Card info present"
            })

        if product and str(product).strip() in ("W", "H", "S"):
            rules.append({
                "rule_id": "RULE_RISKY_PRODUCT",
                "name": "Higher Risk Product Category",
                "severity": "LOW",
                "score_contribution": 5,
                "triggered": True,
                "reason": f"Product code '{product}' associated with elevated risk"
            })
            rule_score += 5
        else:
            rules.append({
                "rule_id": "RULE_RISKY_PRODUCT",
                "name": "Normal Product Category",
                "severity": "LOW",
                "score_contribution": 0,
                "triggered": False,
                "reason": "Normal product category"
            })

        rule_score = max(0, min(100, rule_score))

        return rule_score, rules


class IEEERiskService:
    """IEEE-CIS Risk Inference Service."""

    _instance: Optional["IEEERiskService"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.model = None
        self.preprocessor = None
        self.explainer = None
        self.feature_names: List[str] = []
        self.rule_engine = IEEE_CIS_RuleEngine()

        self.ml_weight = ML_WEIGHT
        self.rule_weight = RULE_WEIGHT
        self.low_threshold = LOW_THRESHOLD
        self.high_threshold = HIGH_THRESHOLD

        self.model_version = "risk_model_v1"
        self.preprocessor_version = "v1"

        self._load_artifacts()
        self._initialized = True

    def _load_artifacts(self) -> None:
        """Load model and preprocessor artifacts."""
        import joblib
        import shap

        logger.info("Loading IEEE-CIS model from: %s", MODEL_PATH)

        if not MODEL_PATH.exists():
            logger.error("Model not found at: %s", MODEL_PATH)
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

        model_artifact = joblib.load(MODEL_PATH)
        self.model = model_artifact["model"]
        self.model_version = model_artifact.get("model_version", "unknown")

        logger.info("Loading preprocessor from: %s", PREPROCESSOR_PATH)

        if not PREPROCESSOR_PATH.exists():
            logger.error("Preprocessor not found at: %s", PREPROCESSOR_PATH)
            raise FileNotFoundError(f"Preprocessor not found at {PREPROCESSOR_PATH}")

        self.preprocessor = joblib.load(PREPROCESSOR_PATH)

        try:
            self.feature_names = self.preprocessor.get_feature_names_out().tolist()
            logger.info("Loaded %d feature names", len(self.feature_names))
        except Exception as e:
            logger.warning("Could not get feature names: %s", e)
            self.feature_names = []

        self.explainer = shap.TreeExplainer(self.model)
        logger.info("Built SHAP TreeExplainer")

        logger.info("IEEE-CIS risk service initialized successfully")

    @staticmethod
    def map_transformed_name(name: str) -> str:
        """Map transformed feature name back to original."""
        if name.startswith("num__"):
            return name[5:]
        elif name.startswith("cat__"):
            parts = name[5:].split("_", 1)
            if len(parts) == 2 and parts[1].isdigit():
                return parts[0]
            return name[5:]
        return name

    def _build_features(self, transaction: Dict[str, Any]) -> pd.DataFrame:
        """Build IEEE-CIS features from transaction input."""
        features: Dict[str, Any] = {}

        amount = transaction.get("TransactionAmt", 0)
        features["amount"] = float(amount)
        features["amount_log"] = float(np.log1p(amount))

        dt = transaction.get("TransactionDT", 0)
        features["transaction_time"] = float(dt)
        features["transaction_hour"] = float((dt / 3600) % 24)
        features["transaction_day"] = float((dt / 86400) % 7)
        features["transaction_day_of_week"] = float((dt / 86400) % 7)

        product = transaction.get("ProductCD")
        if product:
            features["product_code"] = str(product)
        else:
            features["product_code"] = "missing"

        card_cols = ["card1", "card2", "card3", "card4", "card5", "card6"]
        for col in card_cols:
            val = transaction.get(col)
            if val is not None:
                if isinstance(val, (int, float)) and not np.isnan(val):
                    features[col] = float(val)
                else:
                    features[col] = str(val)
            else:
                features[col] = np.nan

        addr1 = transaction.get("addr1")
        if addr1 is not None and isinstance(addr1, (int, float)) and not np.isnan(addr1):
            features["addr1"] = float(addr1)
        else:
            features["addr1"] = np.nan

        addr2 = transaction.get("addr2")
        if addr2 is not None and isinstance(addr2, (int, float)) and not np.isnan(addr2):
            features["addr2"] = float(addr2)
        else:
            features["addr2"] = np.nan

        p_email = transaction.get("P_emaildomain")
        features["P_emaildomain"] = str(p_email) if p_email else "missing"

        r_email = transaction.get("R_emaildomain")
        features["R_emaildomain"] = str(r_email) if r_email else "missing"

        device_type = transaction.get("DeviceType")
        if device_type and str(device_type).strip():
            features["device_type_present"] = 1
            features["DeviceType"] = str(device_type)
        else:
            features["device_type_present"] = 0
            features["DeviceType"] = "missing"

        device_info = transaction.get("DeviceInfo")
        if device_info and str(device_info).strip():
            features["device_info_present"] = 1
            features["DeviceInfo"] = str(device_info)
        else:
            features["device_info_present"] = 0
            features["DeviceInfo"] = "missing"

        p_email = transaction.get("P_emaildomain")
        if p_email and str(p_email).strip():
            features["billing_email_present"] = 1
        else:
            features["billing_email_present"] = 0

        r_email = transaction.get("R_emaildomain")
        if r_email and str(r_email).strip():
            features["recipient_email_present"] = 1
        else:
            features["recipient_email_present"] = 0

        for i in range(1, 15):
            col = f"C{i}"
            val = transaction.get(col)
            if val is not None and isinstance(val, (int, float)) and not np.isnan(val):
                features[col] = float(val)
            else:
                features[col] = np.nan

        for i in range(1, 16):
            col = f"D{i}"
            val = transaction.get(col)
            if val is not None and isinstance(val, (int, float)) and not np.isnan(val):
                features[col] = float(val)
            else:
                features[col] = np.nan

        for i in range(1, 10):
            col = f"M{i}"
            val = transaction.get(col)
            if val is not None and not (isinstance(val, float) and np.isnan(val)):
                features[col] = str(val)
            else:
                features[col] = "missing"

        for i in range(1, 11):
            col = f"V{i}"
            val = transaction.get(col)
            if val is not None and isinstance(val, (int, float)) and not np.isnan(val):
                features[col] = float(val)
            else:
                features[col] = np.nan

        df = pd.DataFrame([features])
        return df

    def _ensure_preprocessor_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure df has all columns expected by preprocessor."""
        expected_cols = set()
        for name, trans, cols in self.preprocessor.transformers:
            expected_cols.update(cols)

        current_cols = set(df.columns)
        missing_cols = expected_cols - current_cols

        if missing_cols:
            df = df.copy()
            for col in missing_cols:
                df[col] = np.nan

        return df

    def assess(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Perform complete risk assessment on a transaction."""
        if self.model is None or self.preprocessor is None:
            raise RuntimeError("Model or preprocessor not loaded")

        feature_df = self._build_features(transaction)
        feature_df = self._ensure_preprocessor_columns(feature_df)

        X_transformed = self.preprocessor.transform(feature_df)

        ml_proba = float(self.model.predict_proba(X_transformed)[0][1])
        ml_score = float(ml_proba * 100)

        rule_score, triggered_rules = self.rule_engine.evaluate(feature_df.iloc[0].to_dict())

        final_score = (
            self.ml_weight * ml_score +
            self.rule_weight * rule_score
        )
        final_score = max(0, min(100, final_score))

        if final_score >= self.high_threshold:
            risk_level = "HIGH"
        elif final_score >= self.low_threshold:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        if risk_level == "HIGH":
            decision = "BLOCK"
        elif risk_level == "MEDIUM":
            decision = "REVIEW"
        else:
            decision = "ALLOW"

        shap_output = self.explainer(X_transformed)
        shap_values = shap_output.values[0]
        shap_dict = {}
        for i, name in enumerate(self.feature_names):
            shap_dict[name] = float(shap_values[i])

        sorted_features = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)

        positive = []
        negative = []

        for name, value in sorted_features:
            contributor = {
                "feature_name": self.map_transformed_name(name),
                "shap_value": value,
                "direction": "increases_risk" if value > 0 else "decreases_risk",
            }

            if value > 0 and len(positive) < 10:
                positive.append(contributor)
            elif value < 0 and len(negative) < 10:
                negative.append(contributor)

        rule_reasons = [
            r["reason"] for r in triggered_rules
            if r["triggered"] and r["score_contribution"] > 0
        ]

        triggered_count = sum(1 for r in triggered_rules if r["triggered"] and r["score_contribution"] > 0)
        if triggered_count == 0:
            explanation = "Risk assessment is primarily based on the ML model."
        else:
            explanation = f"Risk score is elevated due to {triggered_count} triggered rule(s) and ML model probability."

        return {
            "risk_score": round(final_score, 2),
            "risk_level": risk_level,
            "decision": decision,
            "ml_probability": round(ml_proba, 4),
            "ml_score": round(ml_score, 2),
            "rule_score": round(rule_score, 2),
            "triggered_rules": triggered_rules,
            "rule_reasons": rule_reasons,
            "top_positive_features": positive,
            "top_negative_features": negative,
            "explanation": explanation,
            "model_version": self.model_version,
            "preprocessor_version": self.preprocessor_version,
        }

    def health_check(self) -> Dict[str, Any]:
        """Return health status of the service."""
        return {
            "status": "ready" if self.model is not None else "error",
            "model_loaded": self.model is not None,
            "preprocessor_loaded": self.preprocessor is not None,
            "model_version": self.model_version,
            "preprocessor_version": self.preprocessor_version,
        }


def get_ieee_risk_service() -> IEEERiskService:
    """Get the singleton IEEE risk service instance."""
    return IEEERiskService()
