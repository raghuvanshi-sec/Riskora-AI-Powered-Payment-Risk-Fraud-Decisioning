"""
Phase 6.5D — SHAP Explainability Test Script
=============================================

Tests the SHAP explainer implementation using real IEEE-CIS data.
"""

from __future__ import annotations

import json
import logging
import sys
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

TRAIN_TRANSACTION_PATH = DATA_DIR / "train_transaction.csv"
TRAIN_IDENTITY_PATH = DATA_DIR / "train_identity.csv"

PREPROCESSOR_PATH = ML_ARTIFACTS_DIR / "preprocessor_ieee_cis_v1.joblib"
MODEL_PATH = ML_ARTIFACTS_DIR / "risk_model_v1.joblib"

TEST_SAMPLE_SIZE = 5000
GLOBAL_SHAP_SAMPLE_SIZE = 1000


def load_ieee_cis_data(
    transaction_path: Path,
    identity_path: Path,
    sample_size: Optional[int] = None,
) -> Tuple[pd.DataFrame, pd.Series, int]:
    """Load and merge IEEE-CIS transaction and identity data."""
    logger.info("Loading transaction data from: %s", transaction_path)

    if sample_size is not None:
        trans_df = pd.read_csv(transaction_path, nrows=sample_size)
        logger.info("Loaded sample of %d transaction rows", len(trans_df))
    else:
        trans_df = pd.read_csv(transaction_path)
        logger.info("Loaded %d transaction rows", len(trans_df))

    logger.info("Loading identity data from: %s", identity_path)
    id_df = pd.read_csv(identity_path)
    logger.info("Loaded %d identity rows", len(id_df))

    original_count = len(trans_df)

    logger.info("Merging on TransactionID (left join)")
    merged_df = trans_df.merge(id_df, on="TransactionID", how="left")

    if "isFraud" not in merged_df.columns:
        raise ValueError("isFraud column not found in training data")

    target = merged_df["isFraud"]

    return merged_df, target, original_count


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

    feature_df = pd.DataFrame(features)
    logger.info("Built %d features", len(feature_df.columns))

    return feature_df


def filter_valid_features(
    X_train: pd.DataFrame,
    X_val: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str], List[str], List[str]]:
    """Remove features with 100% missing values in X_train."""
    all_cols = X_train.columns.tolist()
    missing_counts = X_train.isna().sum()
    all_missing = missing_counts[missing_counts == len(X_train)].index.tolist()

    if all_missing:
        logger.info("Excluding %d features with all missing values: %s", len(all_missing), all_missing)

    valid_cols = [col for col in all_cols if col not in all_missing]
    excluded_cols = all_missing

    numeric_cols = [col for col in valid_cols if X_train[col].dtype in [np.float32, np.float64, np.int32, np.int64]]
    categorical_cols = [col for col in valid_cols if X_train[col].dtype.name in ["category", "object"]]

    X_train_filtered = X_train[valid_cols]
    X_val_filtered = X_val[valid_cols]

    return X_train_filtered, X_val_filtered, numeric_cols, categorical_cols, excluded_cols


def temporal_split(
    df: pd.DataFrame,
    target: pd.Series,
    test_size: float = 0.2,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Perform temporal train/validation split based on TransactionDT."""
    if "transaction_time" not in df.columns:
        raise ValueError("transaction_time column required for temporal split")

    sort_idx = df["transaction_time"].argsort()
    sorted_df = df.iloc[sort_idx].reset_index(drop=True)
    sorted_target = target.iloc[sort_idx].reset_index(drop=True)

    n = len(sorted_df)
    split_idx = int(n * (1 - test_size))

    X_train = sorted_df.iloc[:split_idx].copy()
    X_val = sorted_df.iloc[split_idx:].copy()
    y_train = sorted_target.iloc[:split_idx].copy()
    y_val = sorted_target.iloc[split_idx:].copy()

    return X_train, X_val, y_train, y_val


def load_model_and_preprocessor():
    """Load model and preprocessor artifacts."""
    import joblib

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

    if not PREPROCESSOR_PATH.exists():
        raise FileNotFoundError(f"Preprocessor not found at {PREPROCESSOR_PATH}")

    model_artifact = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)

    model = model_artifact["model"]
    model_name = model_artifact.get("model_name", "unknown")
    model_version = model_artifact.get("model_version", "unknown")

    logger.info("Loaded model: %s (%s)", model_name, model_version)
    logger.info("Loaded preprocessor from: %s", PREPROCESSOR_PATH)

    return model, preprocessor, model_name, model_version


def get_transformed_feature_names(preprocessor) -> List[str]:
    """Get meaningful feature names from the preprocessor."""
    try:
        feature_names = preprocessor.get_feature_names_out()
        return feature_names.tolist()
    except Exception as e:
        logger.warning("Could not get feature names from preprocessor: %s", e)
        return []


def map_transformed_name_to_original(transformed_name: str) -> str:
    """Map transformed feature name back to original IEEE-CIS feature."""
    if transformed_name.startswith("num__"):
        return transformed_name[5:]
    elif transformed_name.startswith("cat__"):
        parts = transformed_name[5:].split("_", 1)
        if len(parts) == 2 and parts[1].isdigit():
            return parts[0]
        return transformed_name[5:]
    return transformed_name


def explain_single_prediction(
    model,
    preprocessor,
    feature_vector: np.ndarray,
    feature_names: List[str],
) -> Dict[str, Any]:
    """Generate SHAP explanation for a single prediction."""
    import shap

    explainer = shap.TreeExplainer(model)

    shap_output = explainer(feature_vector)

    shap_values = shap_output.values[0]
    base_value = shap_output.base_values[0]

    shap_dict = {}
    for i, name in enumerate(feature_names):
        shap_dict[name] = float(shap_values[i])

    return {
        "shap_values": shap_dict,
        "base_value": float(base_value),
        "expected_value": float(base_value),
    }


def get_top_contributors(
    shap_dict: Dict[str, float],
    top_n: int = 10,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Get top positive and negative SHAP contributors."""
    sorted_features = sorted(
        shap_dict.items(),
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
            "original_name": map_transformed_name_to_original(name),
            "shap_value": value,
            "direction": "increases_risk" if value > 0 else "decreases_risk",
        }

        if value > 0 and len(positive) < top_n:
            positive.append(contributor)
        elif value < 0 and len(negative) < top_n:
            negative.append(contributor)

    return positive, negative


def generate_explanation_text(
    contributor: Dict[str, Any],
) -> str:
    """Generate human-readable explanation for a SHAP contributor."""
    original_name = contributor["original_name"]
    shap_value = contributor["shap_value"]
    direction = contributor["direction"]

    if direction == "increases_risk":
        return f"{original_name} increased the model's predicted fraud risk (SHAP: {shap_value:.4f})"
    else:
        return f"{original_name} decreased the model's predicted fraud risk (SHAP: {shap_value:.4f})"


def validate_shap_reconstruction(
    base_value: float,
    shap_values: np.ndarray,
    model_output: float,
    tolerance: float = 1.0,
) -> Tuple[bool, float]:
    """Validate SHAP reconstruction: base_value + sum(shap_values) should be close to raw margin.

    For XGBoost with binary classification, TreeExplainer returns the margin (log-odds)
    in base_values, not the probability. The sum of SHAP values should approximate
    the difference between the raw model output and the base value.
    """
    shap_sum = float(np.sum(shap_values))
    reconstruction = base_value + shap_sum

    raw_margin = model_output
    error = abs(reconstruction - raw_margin)
    passed = error < tolerance

    logger.info(
        "SHAP reconstruction check: base=%.4f + sum=%.4f = %.4f (margin), model_raw=%.4f, error=%.4f, tolerance=%.4f, PASSED=%s",
        base_value, shap_sum, reconstruction, raw_margin, error, tolerance, passed
    )

    return passed, error


def calculate_global_importance(
    model,
    X_sample: np.ndarray,
    feature_names: List[str],
    sample_size: int = 1000,
) -> List[Dict[str, Any]]:
    """Calculate global SHAP importance using a sample."""
    import shap

    logger.info("Calculating global SHAP importance with %d samples", sample_size)

    explainer = shap.TreeExplainer(model)

    indices = np.random.RandomState(42).choice(len(X_sample), min(sample_size, len(X_sample)), replace=False)
    X_sample_subset = X_sample[indices]

    shap_output = explainer(X_sample_subset)

    mean_abs_shap = np.mean(np.abs(shap_output.values), axis=0)

    importance = []
    for i, name in enumerate(feature_names):
        importance.append({
            "transformed_name": name,
            "original_name": map_transformed_name_to_original(name),
            "mean_abs_shap": float(mean_abs_shap[i]),
        })

    importance.sort(key=lambda x: x["mean_abs_shap"], reverse=True)

    for rank, imp in enumerate(importance):
        imp["rank"] = rank + 1

    return importance


def save_global_importance_report(importance: List[Dict[str, Any]], sample_size: int) -> Path:
    """Save global SHAP importance report."""
    report = {
        "dataset": "ieee_cis",
        "model": "xgboost",
        "sample_size": sample_size,
        "feature_importance": importance,
    }

    report_path = ML_REPORTS_DIR / "shap_global_importance.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    logger.info("Saved global importance report to: %s", report_path)
    return report_path


def save_validation_report(
    model_probability: float,
    base_value: float,
    shap_sum: float,
    reconstructed_output: float,
    reconstruction_error: float,
    prediction_consistency: bool,
    validation_status: str,
) -> Path:
    """Save SHAP validation report."""
    report = {
        "model_probability": float(model_probability),
        "base_value": float(base_value),
        "shap_sum": float(shap_sum),
        "reconstructed_output": float(reconstructed_output),
        "reconstruction_error": float(reconstruction_error),
        "prediction_consistency": bool(prediction_consistency),
        "validation_status": str(validation_status),
    }

    report_path = ML_REPORTS_DIR / "shap_validation_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    logger.info("Saved validation report to: %s", report_path)
    return report_path


def run_shap_test():
    """Run the complete SHAP test."""
    print("=" * 60)
    print("PHASE 6.5D — SHAP EXPLAINABILITY")
    print("=" * 60)

    logger.info("Loading model and preprocessor")
    model, preprocessor, model_name, model_version = load_model_and_preprocessor()

    print(f"\nModel: {model_name}")
    print(f"Model artifact: {MODEL_PATH}")
    print(f"Preprocessor: {PREPROCESSOR_PATH}")

    feature_names = get_transformed_feature_names(preprocessor)
    print(f"Transformed feature count: {len(feature_names)}")

    logger.info("Loading IEEE-CIS validation data")
    merged_df, target, original_count = load_ieee_cis_data(
        TRAIN_TRANSACTION_PATH,
        TRAIN_IDENTITY_PATH,
        sample_size=TEST_SAMPLE_SIZE,
    )

    logger.info("Building features")
    feature_df = build_ieee_cis_features(merged_df)

    logger.info("Performing temporal split")
    X_train_raw, X_val_raw, y_train, y_val = temporal_split(feature_df, target, test_size=0.2)

    logger.info("Filtering features")
    X_train, X_val, numeric_cols, categorical_cols, excluded_cols = filter_valid_features(
        X_train_raw, X_val_raw
    )

    logger.info("Transforming validation data")
    X_val_transformed = preprocessor.transform(X_val)

    print(f"\nValidation sample: {len(X_val_transformed)} rows")

    sample_idx = 0
    feature_vector = X_val_transformed[sample_idx:sample_idx+1]

    logger.info("Generating SHAP explanation for sample transaction")
    shap_result = explain_single_prediction(model, preprocessor, feature_vector, feature_names)

    model_proba = float(model.predict_proba(feature_vector)[0][1])
    model_pred = int(model.predict(feature_vector)[0])

    print(f"\nModel probability: {model_proba:.4f}")
    print(f"Prediction class: {model_pred}")

    base_value = shap_result["base_value"]
    shap_values = shap_result["shap_values"]
    shap_values_array = np.array(list(shap_values.values()))

    print(f"Base value: {base_value:.4f}")
    print(f"SHAP sum: {np.sum(shap_values_array):.4f}")

    import math
    raw_margin = math.log(model_proba / (1 - model_proba + 1e-10))
    reconstruction_passed, reconstruction_error = validate_shap_reconstruction(
        base_value,
        shap_values_array,
        raw_margin,
        tolerance=1.0,
    )

    shap_sum = float(np.sum(shap_values_array))
    shap_contribution = base_value + shap_sum
    expected_proba = 1 / (1 + math.exp(-shap_contribution))
    prediction_consistency = abs(model_proba - expected_proba) < 0.01

    print(f"\nRaw margin: {raw_margin:.4f}")
    print(f"Expected proba from SHAP: {expected_proba:.4f}")
    print(f"SHAP reconstruction: {'PASSED' if reconstruction_passed else 'FAILED'}")
    print(f"Prediction consistency: {'PASSED' if prediction_consistency else 'FAILED'}")

    positive_contributors, negative_contributors = get_top_contributors(shap_values, top_n=10)

    print("\n" + "=" * 60)
    print("TOP POSITIVE CONTRIBUTORS")
    print("=" * 60)
    for i, contrib in enumerate(positive_contributors[:10], 1):
        print(f"{i}. {generate_explanation_text(contrib)}")

    print("\n" + "=" * 60)
    print("TOP NEGATIVE CONTRIBUTORS")
    print("=" * 60)
    for i, contrib in enumerate(negative_contributors[:10], 1):
        print(f"{i}. {generate_explanation_text(contrib)}")

    logger.info("Calculating global SHAP importance")
    global_importance = calculate_global_importance(
        model,
        X_val_transformed,
        feature_names,
        sample_size=GLOBAL_SHAP_SAMPLE_SIZE,
    )

    print("\n" + "=" * 60)
    print("GLOBAL SHAP IMPORTANCE")
    print("=" * 60)
    for imp in global_importance[:15]:
        print(f"{imp['rank']}. {imp['original_name']}: {imp['mean_abs_shap']:.4f}")

    importance_path = save_global_importance_report(global_importance, GLOBAL_SHAP_SAMPLE_SIZE)

    validation_status = "PASSED" if (reconstruction_passed and prediction_consistency) else "FAILED"
    validation_path = save_validation_report(
        model_probability=model_proba,
        base_value=base_value,
        shap_sum=float(np.sum(shap_values_array)),
        reconstructed_output=base_value + float(np.sum(shap_values_array)),
        reconstruction_error=reconstruction_error,
        prediction_consistency=prediction_consistency,
        validation_status=validation_status,
    )

    print("\n" + "=" * 60)
    print("REPORTS")
    print("=" * 60)
    print(f"shap_global_importance.json: {importance_path}")
    print(f"shap_validation_report.json: {validation_path}")

    print("\n" + "=" * 60)
    print("PHASE 6.5D COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_shap_test()
