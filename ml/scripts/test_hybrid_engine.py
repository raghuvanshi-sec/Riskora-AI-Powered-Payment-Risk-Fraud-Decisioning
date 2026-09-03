"""
Phase 6.5E — Hybrid Risk Engine for Riskora
============================================

Combines:
1. Deterministic fraud/risk rules (IEEE-CIS based)
2. XGBoost ML probability
3. SHAP explanation

into a final risk assessment.
"""

from __future__ import annotations

import json
import logging
import math
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "ieee_cis"
ML_ARTIFACTS_DIR = PROJECT_ROOT / "ml" / "artifacts"
ML_REPORTS_DIR = PROJECT_ROOT / "ml" / "reports"

ML_WEIGHT = 0.70
RULE_WEIGHT = 0.30

LOW_THRESHOLD = 30
HIGH_THRESHOLD = 70

AMOUNT_HIGH_THRESHOLD = 300.0
AMOUNT_LOG_HIGH_THRESHOLD = 5.7
TRANSACTION_HOUR_SUSPICIOUS = 3
DEVICE_TYPE_THRESHOLD = 0.5


@dataclass
class RuleResult:
    rule_id: str
    name: str
    description: str
    severity: str
    score_contribution: int
    triggered: bool
    reason: str


@dataclass
class RiskAssessment:
    risk_score: float
    risk_level: str
    decision: str
    ml_probability: float
    ml_score: float
    rule_score: float
    triggered_rules: List[Dict[str, Any]]
    rule_reasons: List[str]
    top_positive_features: List[Dict[str, Any]]
    top_negative_features: List[Dict[str, Any]]
    explanation: str


class IEEE_CIS_RuleEngine:
    """Deterministic rule engine for IEEE-CIS transactions."""

    def __init__(self):
        self.rules: List[RuleResult] = []

    def evaluate(self, transaction: pd.Series, feature_df: pd.DataFrame) -> Tuple[float, List[RuleResult]]:
        """Evaluate all applicable rules."""
        self.rules = []

        self._check_high_amount(transaction)
        self._check_unusual_hour(transaction)
        self._check_missing_email(transaction)
        self._check_missing_device(transaction)
        self._check_missing_card_info(transaction)
        self._check_product_risk(transaction)
        self._check_address_anomaly(feature_df)

        rule_score = sum(r.score_contribution for r in self.rules if r.triggered)
        rule_score = max(0, min(100, rule_score))

        return rule_score, self.rules

    def _check_high_amount(self, tx: pd.Series) -> None:
        """Check for unusually high transaction amount."""
        amount = tx.get("amount", 0)
        amount_log = tx.get("amount_log", 0)

        if pd.notna(amount) and amount > AMOUNT_HIGH_THRESHOLD:
            self.rules.append(RuleResult(
                rule_id="RULE_HIGH_AMOUNT",
                name="High Transaction Amount",
                description="Transaction amount exceeds configured threshold",
                severity="HIGH",
                score_contribution=20,
                triggered=True,
                reason=f"Transaction amount ${amount:.2f} exceeds threshold ${AMOUNT_HIGH_THRESHOLD}"
            ))
        elif pd.notna(amount_log) and amount_log > AMOUNT_LOG_HIGH_THRESHOLD:
            self.rules.append(RuleResult(
                rule_id="RULE_HIGH_AMOUNT",
                name="High Transaction Amount",
                description="Transaction amount log exceeds threshold",
                severity="MEDIUM",
                score_contribution=15,
                triggered=True,
                reason=f"Transaction amount log {amount_log:.2f} exceeds threshold"
            ))
        else:
            self.rules.append(RuleResult(
                rule_id="RULE_HIGH_AMOUNT",
                name="High Transaction Amount",
                description="Transaction amount within normal range",
                severity="LOW",
                score_contribution=0,
                triggered=False,
                reason="Amount within normal range"
            ))

    def _check_unusual_hour(self, tx: pd.Series) -> None:
        """Check for unusual transaction hour (late night/early morning)."""
        hour = tx.get("transaction_hour", None)

        if pd.notna(hour) and hour < TRANSACTION_HOUR_SUSPICIOUS:
            self.rules.append(RuleResult(
                rule_id="RULE_UNUSUAL_HOUR",
                name="Unusual Transaction Hour",
                description="Transaction occurred during suspicious hours (3AM-6AM)",
                severity="MEDIUM",
                score_contribution=10,
                triggered=True,
                reason=f"Transaction at hour {hour:.2f} is unusual"
            ))
        else:
            self.rules.append(RuleResult(
                rule_id="RULE_UNUSUAL_HOUR",
                name="Unusual Transaction Hour",
                description="Transaction time is within normal hours",
                severity="LOW",
                score_contribution=0,
                triggered=False,
                reason="Normal transaction hour"
            ))

    def _check_missing_email(self, tx: pd.Series) -> None:
        """Check for missing or mismatched email information."""
        p_email = tx.get("P_emaildomain", None)
        r_email = tx.get("R_emaildomain", None)

        p_present = pd.notna(p_email) and str(p_email).strip() not in ("", "missing")
        r_present = pd.notna(r_email) and str(r_email).strip() not in ("", "missing")

        if not p_present:
            self.rules.append(RuleResult(
                rule_id="RULE_MISSING_BILLING_EMAIL",
                name="Missing Billing Email",
                description="Billing email is missing",
                severity="LOW",
                score_contribution=5,
                triggered=True,
                reason="Billing email is missing or invalid"
            ))
        else:
            self.rules.append(RuleResult(
                rule_id="RULE_MISSING_BILLING_EMAIL",
                name="Missing Billing Email",
                description="Billing email is present",
                severity="LOW",
                score_contribution=0,
                triggered=False,
                reason="Billing email present"
            ))

        if p_present and r_present and p_email != r_email:
            self.rules.append(RuleResult(
                rule_id="RULE_EMAIL_MISMATCH",
                name="Email Domain Mismatch",
                description="Billing and recipient email domains differ",
                severity="MEDIUM",
                score_contribution=15,
                triggered=True,
                reason=f"Billing email ({p_email}) differs from recipient ({r_email})"
            ))
        else:
            self.rules.append(RuleResult(
                rule_id="RULE_EMAIL_MISMATCH",
                name="Email Domain Mismatch",
                description="Email domains match or not applicable",
                severity="LOW",
                score_contribution=0,
                triggered=False,
                reason="Email domains match or N/A"
            ))

    def _check_missing_device(self, tx: pd.Series) -> None:
        """Check for missing device information."""
        device_type_present = tx.get("device_type_present", 0)
        device_info_present = tx.get("device_info_present", 0)

        if pd.notna(device_type_present) and device_type_present < DEVICE_TYPE_THRESHOLD:
            self.rules.append(RuleResult(
                rule_id="RULE_MISSING_DEVICE",
                name="Missing Device Information",
                description="Device type information is missing",
                severity="MEDIUM",
                score_contribution=10,
                triggered=True,
                reason="Device type is missing"
            ))
        else:
            self.rules.append(RuleResult(
                rule_id="RULE_MISSING_DEVICE",
                name="Missing Device Information",
                description="Device information is present",
                severity="LOW",
                score_contribution=0,
                triggered=False,
                reason="Device information present"
            ))

        if pd.notna(device_info_present) and device_info_present < DEVICE_TYPE_THRESHOLD:
            self.rules.append(RuleResult(
                rule_id="RULE_MISSING_DEVICE_INFO",
                name="Missing Device Info",
                description="Specific device info is missing",
                severity="LOW",
                score_contribution=5,
                triggered=True,
                reason="Device info is missing"
            ))
        else:
            self.rules.append(RuleResult(
                rule_id="RULE_MISSING_DEVICE_INFO",
                name="Missing Device Info",
                description="Device info is present",
                severity="LOW",
                score_contribution=0,
                triggered=False,
                reason="Device info present"
            ))

    def _check_missing_card_info(self, tx: pd.Series) -> None:
        """Check for missing card information."""
        card2_present = pd.notna(tx.get("card2", None))
        card3_present = pd.notna(tx.get("card3", None))

        missing_count = 0
        if not card2_present:
            missing_count += 1
        if not card3_present:
            missing_count += 1

        if missing_count >= 2:
            self.rules.append(RuleResult(
                rule_id="RULE_MISSING_CARD_INFO",
                name="Missing Card Information",
                description="Multiple card fields are missing",
                severity="MEDIUM",
                score_contribution=10,
                triggered=True,
                reason=f"{missing_count} card fields missing"
            ))
        else:
            self.rules.append(RuleResult(
                rule_id="RULE_MISSING_CARD_INFO",
                name="Missing Card Information",
                description="Card information is sufficient",
                severity="LOW",
                score_contribution=0,
                triggered=False,
                reason="Card info present"
            ))

    def _check_product_risk(self, tx: pd.Series) -> None:
        """Check for risky product codes."""
        product = tx.get("product_code", None)

        if pd.notna(product) and str(product).strip() in ("W", "H", "S"):
            self.rules.append(RuleResult(
                rule_id="RULE_RISKY_PRODUCT",
                name="Higher Risk Product Category",
                description="Transaction involves higher-risk product category",
                severity="LOW",
                score_contribution=5,
                triggered=True,
                reason=f"Product code '{product}' associated with elevated risk"
            ))
        else:
            self.rules.append(RuleResult(
                rule_id="RULE_RISKY_PRODUCT",
                name="Normal Product Category",
                description="Product category is standard",
                severity="LOW",
                score_contribution=0,
                triggered=False,
                reason="Normal product category"
            ))

    def _check_address_anomaly(self, feature_df: pd.DataFrame) -> None:
        """Check for address anomalies based on distribution."""
        addr1 = feature_df.get("addr1", None)
        addr2 = feature_df.get("addr2", None)

        if addr1 is not None and len(addr1) > 0:
            addr1_std = float(addr1.std()) if addr1.dtype in [np.float32, np.float64] else 0
            if addr1_std > 100:
                self.rules.append(RuleResult(
                    rule_id="RULE_ADDRESS_ANOMALY",
                    name="Address Distribution Anomaly",
                    description="High variance in address field suggests unusual activity",
                    severity="LOW",
                    score_contribution=5,
                    triggered=True,
                    reason="Address field shows high variance"
                ))
            else:
                self.rules.append(RuleResult(
                    rule_id="RULE_ADDRESS_ANOMALY",
                    name="Address Normal",
                    description="Address distribution is normal",
                    severity="LOW",
                    score_contribution=0,
                    triggered=False,
                    reason="Normal address distribution"
                ))
        else:
            self.rules.append(RuleResult(
                rule_id="RULE_ADDRESS_ANOMALY",
                name="Address N/A",
                description="Address check not applicable",
                severity="LOW",
                score_contribution=0,
                triggered=False,
                reason="Address data not available"
            ))


class HybridRiskEngine:
    """Hybrid Risk Engine combining ML and rules."""

    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.explainer = None
        self.feature_names: List[str] = []
        self.rule_engine = IEEE_CIS_RuleEngine()

        self.ml_weight = ML_WEIGHT
        self.rule_weight = RULE_WEIGHT
        self.low_threshold = LOW_THRESHOLD
        self.high_threshold = HIGH_THRESHOLD

        self._validate_weights()

    def _validate_weights(self) -> None:
        """Validate that weights sum to 1.0."""
        if abs(self.ml_weight + self.rule_weight - 1.0) > 0.001:
            raise ValueError(
                f"ML_WEIGHT ({self.ml_weight}) + RULE_WEIGHT ({self.rule_weight}) must equal 1.0"
            )

    def load_model(self, model_path: Optional[Path] = None) -> None:
        """Load the XGBoost model."""
        import joblib

        if model_path is None:
            model_path = ML_ARTIFACTS_DIR / "risk_model_v1.joblib"

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found at {model_path}")

        model_artifact = joblib.load(model_path)
        self.model = model_artifact["model"]
        logger.info("Loaded model: %s", model_artifact.get("model_name", "unknown"))

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
        """Get transformed feature names."""
        if self.preprocessor is None:
            return []

        try:
            self.feature_names = self.preprocessor.get_feature_names_out().tolist()
        except Exception as e:
            logger.warning("Could not get feature names: %s", e)
            self.feature_names = []

        return self.feature_names

    def build_explainer(self) -> None:
        """Build the SHAP TreeExplainer."""
        import shap

        if self.model is None:
            raise RuntimeError("Model not loaded")

        self.explainer = shap.TreeExplainer(self.model)
        logger.info("Built SHAP TreeExplainer")

    def transform_features(self, X: pd.DataFrame) -> np.ndarray:
        """Transform features using the preprocessor."""
        if self.preprocessor is None:
            raise RuntimeError("Preprocessor not loaded")

        return self.preprocessor.transform(X)

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

    def explain_single(self, X_transformed: np.ndarray) -> Tuple[float, List[Dict], List[Dict]]:
        """Generate SHAP explanation for a single transaction."""
        shap_output = self.explainer(X_transformed)

        shap_values = shap_output.values[0]
        base_value = shap_output.base_values[0]

        shap_dict = {}
        for i, name in enumerate(self.feature_names):
            shap_dict[name] = float(shap_values[i])

        sorted_features = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)

        positive = []
        negative = []

        for name, value in sorted_features:
            contributor = {
                "transformed_name": name,
                "original_name": self.map_transformed_name(name),
                "shap_value": value,
                "direction": "increases_risk" if value > 0 else "decreases_risk",
            }

            if value > 0 and len(positive) < 10:
                positive.append(contributor)
            elif value < 0 and len(negative) < 10:
                negative.append(contributor)

        return float(base_value), shap_dict, positive, negative

    def calculate_ml_score(self, ml_probability: float) -> float:
        """Convert ML probability to 0-100 score."""
        return max(0, min(100, ml_probability * 100))

    def calculate_hybrid_score(self, ml_score: float, rule_score: float) -> float:
        """Combine ML and rule scores into final risk score."""
        final = (
            self.ml_weight * ml_score +
            self.rule_weight * rule_score
        )
        return max(0, min(100, final))

    def get_risk_level(self, risk_score: float) -> str:
        """Determine risk level from score."""
        if risk_score >= self.high_threshold:
            return "HIGH"
        elif risk_score >= self.low_threshold:
            return "MEDIUM"
        return "LOW"

    def get_decision(self, risk_level: str) -> str:
        """Map risk level to operational decision."""
        if risk_level == "HIGH":
            return "BLOCK"
        elif risk_level == "MEDIUM":
            return "REVIEW"
        return "ALLOW"

    def assess(
        self,
        transaction: pd.Series,
        feature_df: pd.DataFrame,
    ) -> RiskAssessment:
        """Perform complete risk assessment."""
        if self.model is None or self.preprocessor is None:
            raise RuntimeError("Model or preprocessor not loaded")

        feature_df = ensure_all_preprocessor_columns(feature_df, self.preprocessor)

        X_transformed = self.transform_features(feature_df)

        ml_proba = float(self.model.predict_proba(X_transformed)[0][1])

        if not 0 <= ml_proba <= 1:
            raise ValueError(f"Invalid ML probability: {ml_proba}")

        ml_score = self.calculate_ml_score(ml_proba)

        rule_score, triggered_rules = self.rule_engine.evaluate(transaction, feature_df)

        risk_score = self.calculate_hybrid_score(ml_score, rule_score)

        risk_level = self.get_risk_level(risk_score)
        decision = self.get_decision(risk_level)

        _, shap_dict, top_positive, top_negative = self.explain_single(X_transformed)

        rule_reasons = [
            r.reason for r in triggered_rules
            if r.triggered and r.score_contribution > 0
        ]

        triggered_rule_info = [
            {
                "rule_id": r.rule_id,
                "name": r.name,
                "severity": r.severity,
                "score_contribution": r.score_contribution,
                "triggered": r.triggered,
                "reason": r.reason,
            }
            for r in triggered_rules
        ]

        triggered_count = sum(1 for r in triggered_rules if r.triggered and r.score_contribution > 0)
        if triggered_count == 0:
            explanation = "Risk assessment is primarily based on the ML model."
        else:
            explanation = f"Risk score is elevated due to {triggered_count} triggered rule(s) and ML model probability."

        return RiskAssessment(
            risk_score=risk_score,
            risk_level=risk_level,
            decision=decision,
            ml_probability=ml_proba,
            ml_score=ml_score,
            rule_score=rule_score,
            triggered_rules=triggered_rule_info,
            rule_reasons=rule_reasons,
            top_positive_features=top_positive,
            top_negative_features=top_negative,
            explanation=explanation,
        )


def build_ieee_cis_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build engineered features from IEEE-CIS data. Must match Phase 6.5B.4."""
    features: Dict[str, Any] = {}

    if "TransactionAmt" in df.columns:
        features["amount"] = df["TransactionAmt"].astype("float32")
        features["amount_log"] = np.log1p(df["TransactionAmt"].astype("float32"))

    if "TransactionDT" in df.columns:
        transaction_dt = pd.to_numeric(df["TransactionDT"], errors="coerce")
        features["transaction_time"] = transaction_dt.astype("float32")
        features["transaction_hour"] = ((transaction_dt / 3600) % 24).astype("float32")
        features["transaction_day"] = ((transaction_dt / 86400) % 7).astype("float32")
        features["transaction_day_of_week"] = ((transaction_dt / 86400) % 7).astype("float32")

    if "ProductCD" in df.columns:
        features["product_code"] = df["ProductCD"].fillna("missing").astype("category")

    card_cols = ["card1", "card2", "card3", "card4", "card5", "card6"]
    for col in card_cols:
        if col in df.columns:
            col_data = df[col]
            if col_data.dtype == object or col_data.dtype.name == "string":
                numeric_vals = pd.to_numeric(col_data, errors="coerce")
                if numeric_vals.notna().mean() > 0.5:
                    features[col] = numeric_vals.astype("float32")
                else:
                    features[col] = col_data.fillna("missing").astype("category")
            else:
                features[col] = pd.to_numeric(col_data, errors="coerce").astype("float32")

    if "addr1" in df.columns:
        addr1_data = df["addr1"]
        if addr1_data.dtype == object or addr1_data.dtype.name == "string":
            numeric_vals = pd.to_numeric(addr1_data, errors="coerce")
            if numeric_vals.notna().mean() > 0.5:
                features["addr1"] = numeric_vals.astype("float32")
            else:
                features["addr1"] = addr1_data.fillna("missing").astype("category")
        else:
            features["addr1"] = pd.to_numeric(addr1_data, errors="coerce").astype("float32")

    if "addr2" in df.columns:
        addr2_data = df["addr2"]
        if addr2_data.dtype == object or addr2_data.dtype.name == "string":
            numeric_vals = pd.to_numeric(addr2_data, errors="coerce")
            if numeric_vals.notna().mean() > 0.5:
                features["addr2"] = numeric_vals.astype("float32")
            else:
                features["addr2"] = addr2_data.fillna("missing").astype("category")
        else:
            features["addr2"] = pd.to_numeric(addr2_data, errors="coerce").astype("float32")

    if "P_emaildomain" in df.columns:
        features["P_emaildomain"] = df["P_emaildomain"].fillna("missing").astype("category")
    if "R_emaildomain" in df.columns:
        features["R_emaildomain"] = df["R_emaildomain"].fillna("missing").astype("category")

    if "DeviceType" in df.columns:
        device_mask = df["DeviceType"].notna() & df["DeviceType"].astype(str).str.strip().ne("")
        features["device_type_present"] = device_mask.astype("int8")
        features["DeviceType"] = df["DeviceType"].fillna("missing").astype("category")
    else:
        features["device_type_present"] = pd.Series(0, index=df.index, dtype="int8")

    if "DeviceInfo" in df.columns:
        device_info_mask = df["DeviceInfo"].notna() & df["DeviceInfo"].astype(str).str.strip().ne("")
        features["device_info_present"] = device_info_mask.astype("int8")
        features["DeviceInfo"] = df["DeviceInfo"].fillna("missing").astype("category")
    else:
        features["device_info_present"] = pd.Series(0, index=df.index, dtype="int8")

    if "P_emaildomain" in df.columns:
        billing_email_mask = df["P_emaildomain"].notna() & df["P_emaildomain"].astype(str).str.strip().ne("")
        features["billing_email_present"] = billing_email_mask.astype("int8")
    else:
        features["billing_email_present"] = pd.Series(0, index=df.index, dtype="int8")

    if "R_emaildomain" in df.columns:
        recipient_email_mask = df["R_emaildomain"].notna() & df["R_emaildomain"].astype(str).str.strip().ne("")
        features["recipient_email_present"] = recipient_email_mask.astype("int8")
    else:
        features["recipient_email_present"] = pd.Series(0, index=df.index, dtype="int8")

    c_cols = [f"C{i}" for i in range(1, 15) if f"C{i}" in df.columns]
    for col in c_cols:
        features[col] = pd.to_numeric(df[col], errors="coerce").astype("float32")

    d_cols = [f"D{i}" for i in range(1, 16) if f"D{i}" in df.columns]
    for col in d_cols:
        features[col] = pd.to_numeric(df[col], errors="coerce").astype("float32")

    m_cols = [f"M{i}" for i in range(1, 10) if f"M{i}" in df.columns]
    for col in m_cols:
        features[col] = df[col].fillna("missing").astype("category")

    v_cols = [f"V{i}" for i in range(1, 11) if f"V{i}" in df.columns]
    for col in v_cols:
        features[col] = pd.to_numeric(df[col], errors="coerce").astype("float32")

    return pd.DataFrame(features)


def filter_valid_features(
    X_train: pd.DataFrame,
    X_val: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str], List[str], List[str]]:
    """Remove features with 100% missing values in X_train."""
    all_cols = X_train.columns.tolist()
    missing_counts = X_train.isna().sum()
    all_missing = missing_counts[missing_counts == len(X_train)].index.tolist()

    valid_cols = [col for col in all_cols if col not in all_missing]
    excluded_cols = all_missing

    X_train_filtered = X_train[valid_cols]
    X_val_filtered = X_val[valid_cols]

    return X_train_filtered, X_val_filtered, [], [], excluded_cols


def ensure_all_preprocessor_columns(
    feature_df: pd.DataFrame,
    preprocessor,
) -> pd.DataFrame:
    """Ensure feature_df has all columns expected by preprocessor input."""
    try:
        expected_cols = set()
        for name, trans, cols in preprocessor.transformers:
            expected_cols.update(cols)
    except Exception:
        return feature_df

    current_cols = set(feature_df.columns)
    missing_cols = expected_cols - current_cols

    if missing_cols:
        feature_df = feature_df.copy()
        for col in missing_cols:
            feature_df[col] = np.nan

    return feature_df


def load_validation_sample(transaction_path: Path, identity_path: Path, n_rows: int = 5) -> Tuple[pd.DataFrame, pd.Series]:
    """Load a small validation sample."""
    trans_df = pd.read_csv(transaction_path, nrows=500)
    id_df = pd.read_csv(identity_path)

    merged = trans_df.merge(id_df, on="TransactionID", how="left")

    if "transaction_time" in merged.columns:
        sort_idx = merged["transaction_time"].argsort()
        merged = merged.iloc[sort_idx].reset_index(drop=True)

    n = len(merged)
    split_idx = int(n * 0.8)

    val_df = merged.iloc[split_idx:split_idx + n_rows].reset_index(drop=True)

    target = val_df["isFraud"] if "isFraud" in val_df.columns else pd.Series([0] * len(val_df))

    return val_df, target


def run_hybrid_engine_test():
    """Run the hybrid engine test."""
    print("=" * 60)
    print("PHASE 6.5E — HYBRID RISK ENGINE")
    print("=" * 60)

    transaction_path = DATA_DIR / "train_transaction.csv"
    identity_path = DATA_DIR / "train_identity.csv"

    print("\nModel: XGBoost")
    print(f"ML Weight: {ML_WEIGHT}")
    print(f"Rule Weight: {RULE_WEIGHT}")
    print(f"\nRisk Thresholds:")
    print(f"  LOW < {LOW_THRESHOLD}")
    print(f"  MEDIUM {LOW_THRESHOLD}-{HIGH_THRESHOLD}")
    print(f"  HIGH >= {HIGH_THRESHOLD}")

    engine = HybridRiskEngine()

    print("\nLoading model and preprocessor...")
    engine.load_model()
    engine.load_preprocessor()
    engine.get_feature_names()
    engine.build_explainer()

    print("\nLoading validation sample...")
    val_df, _ = load_validation_sample(transaction_path, identity_path, n_rows=5)

    print(f"Validation sample: {len(val_df)} transactions")

    print("\n" + "=" * 60)
    print("TRANSACTION TESTS")
    print("=" * 60)

    results = []

    for idx in range(len(val_df)):
        tx = val_df.iloc[idx]

        feature_df = build_ieee_cis_features(val_df.iloc[[idx]])
        feature_df_filtered, _, _, _, _ = filter_valid_features(feature_df, feature_df)

        assessment = engine.assess(tx, feature_df_filtered)

        print(f"\n--- Transaction {idx + 1} ---")
        print(f"Transaction amount: ${tx.get('TransactionAmt', 'N/A')}")
        print(f"ML probability: {assessment.ml_probability:.4f}")
        print(f"ML score: {assessment.ml_score:.2f}")
        print(f"Rule score: {assessment.rule_score:.2f}")
        print(f"Final risk score: {assessment.risk_score:.2f}")
        print(f"Risk level: {assessment.risk_level}")
        print(f"Decision: {assessment.decision}")

        triggered = [r for r in assessment.triggered_rules if r["triggered"] and r["score_contribution"] > 0]
        if triggered:
            print(f"Triggered rules ({len(triggered)}):")
            for r in triggered:
                print(f"  - {r['name']}: {r['reason']}")
        else:
            print("Triggered rules: None")

        if assessment.top_positive_features:
            top_pos = assessment.top_positive_features[0]
            print(f"Top positive SHAP: {top_pos['original_name']} ({top_pos['shap_value']:.4f})")

        if assessment.top_negative_features:
            top_neg = assessment.top_negative_features[0]
            print(f"Top negative SHAP: {top_neg['original_name']} ({top_neg['shap_value']:.4f})")

        print(f"Explanation: {assessment.explanation}")

        validation_passed = True
        validation_passed &= 0 <= assessment.ml_probability <= 1
        validation_passed &= 0 <= assessment.ml_score <= 100
        validation_passed &= 0 <= assessment.rule_score <= 100
        validation_passed &= 0 <= assessment.risk_score <= 100
        validation_passed &= assessment.risk_level in ("LOW", "MEDIUM", "HIGH")
        validation_passed &= assessment.decision in ("ALLOW", "REVIEW", "BLOCK")

        results.append({
            "transaction_index": idx,
            "ml_probability": float(assessment.ml_probability),
            "ml_score": float(assessment.ml_score),
            "rule_score": float(assessment.rule_score),
            "risk_score": float(assessment.risk_score),
            "risk_level": assessment.risk_level,
            "decision": assessment.decision,
            "triggered_rules": [r["rule_id"] for r in triggered],
            "validation_passed": validation_passed,
        })

    print("\n" + "=" * 60)
    print("VALIDATION")
    print("=" * 60)

    all_passed = all(r["validation_passed"] for r in results)
    score_range_passed = all(
        0 <= r["ml_probability"] <= 1 and
        0 <= r["ml_score"] <= 100 and
        0 <= r["rule_score"] <= 100 and
        0 <= r["risk_score"] <= 100
        for r in results
    )

    print(f"Score range: {'PASSED' if score_range_passed else 'FAILED'}")
    print(f"Risk level mapping: {'PASSED' if all_passed else 'FAILED'}")
    print(f"Decision mapping: {'PASSED' if all_passed else 'FAILED'}")

    report = {
        "model": "xgboost",
        "model_version": "risk_model_v1",
        "preprocessor_version": "v1",
        "ml_weight": ML_WEIGHT,
        "rule_weight": RULE_WEIGHT,
        "low_threshold": LOW_THRESHOLD,
        "high_threshold": HIGH_THRESHOLD,
        "test_transaction_count": len(results),
        "results": results,
        "validation_status": "PASSED" if all_passed else "FAILED",
    }

    report_path = ML_REPORTS_DIR / "hybrid_engine_validation.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 60)
    print("REPORT")
    print("=" * 60)
    print(f"Saved: {report_path}")

    print("\n" + "=" * 60)
    print("PHASE 6.5E COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_hybrid_engine_test()
