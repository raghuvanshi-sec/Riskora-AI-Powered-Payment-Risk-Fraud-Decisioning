"""
IEEE-CIS Fraud Detection Feature Engineering Pipeline
====================================================

Production-quality feature engineering for the IEEE-CIS fraud detection dataset.
This script handles data loading, feature engineering, preprocessing, and artifact creation.

Usage:
    python -m ml.scripts.ieee_cis_feature_engineering --help
    python -m ml.scripts.ieee_cis_feature_engineering --test
    python -m ml.scripts.ieee_cis_feature_engineering --full
"""

from __future__ import annotations

import argparse
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
TEST_TRANSACTION_PATH = DATA_DIR / "test_transaction.csv"
TEST_IDENTITY_PATH = DATA_DIR / "test_identity.csv"

TEST_SAMPLE_SIZE = 1000


def ensure_directories() -> None:
    """Create required output directories."""
    ML_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    ML_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Output directories ensured: %s, %s", ML_ARTIFACTS_DIR, ML_REPORTS_DIR)


def load_ieee_cis_data(
    transaction_path: Path,
    identity_path: Path,
    sample_size: Optional[int] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, int]:
    """
    Load and merge IEEE-CIS transaction and identity data.

    Args:
        transaction_path: Path to transaction CSV
        identity_path: Path to identity CSV
        sample_size: If provided, load only this many rows from transaction data

    Returns:
        Tuple of (merged_df, target_series, original_transaction_count)
    """
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
    logger.info(
        "Merge complete: %d merged rows (%d had identity data)",
        len(merged_df),
        merged_df["TransactionID"].nunique(),
    )

    trans_with_id = merged_df["TransactionID"].nunique()
    id_count = id_df["TransactionID"].nunique()
    logger.info(
        "Transactions: %d, Identities: %d, Matched: %d",
        original_count,
        id_count,
        trans_with_id,
    )

    return merged_df, original_count


def build_ieee_cis_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build engineered features from IEEE-CIS data.

    Args:
        df: Merged IEEE-CIS dataframe

    Returns:
        DataFrame with engineered features only
    """
    logger.info("Building IEEE-CIS features")
    features: Dict[str, Any] = {}

    if "TransactionAmt" in df.columns:
        features["amount"] = df["TransactionAmt"].astype("float32")
        features["amount_log"] = np.log1p(df["TransactionAmt"].astype("float32"))
    else:
        logger.warning("TransactionAmt not found")

    if "TransactionDT" in df.columns:
        transaction_dt = pd.to_numeric(df["TransactionDT"], errors="coerce")
        features["transaction_time"] = transaction_dt.astype("float32")
        features["transaction_hour"] = ((transaction_dt / 3600) % 24).astype("float32")
        features["transaction_day"] = ((transaction_dt / 86400) % 7).astype("float32")
        features["transaction_day_of_week"] = ((transaction_dt / 86400) % 7).astype("float32")
    else:
        logger.warning("TransactionDT not found")

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


def validate_features(feature_df: pd.DataFrame, target: Optional[pd.Series] = None) -> None:
    """
    Validate feature matrix for common issues.

    Args:
        feature_df: Engineered features
        target: Optional target series for additional validation

    Raises:
        ValueError: If validation fails
    """
    logger.info("Validating features")

    if feature_df.empty or feature_df.shape[1] == 0:
        raise ValueError("Feature count is 0 - no features to train on")

    if "TransactionID" in feature_df.columns:
        raise ValueError("TransactionID found in feature matrix - must be excluded")

    if target is not None and "isFraud" in feature_df.columns:
        raise ValueError("isFraud found in feature matrix - must be excluded from X")

    numeric_cols = feature_df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        variances = feature_df[numeric_cols].var()
        constant_cols = variances[variances == 0].index.tolist()
        if len(constant_cols) == len(numeric_cols):
            raise ValueError("All numeric features are constant")

    nan_counts = feature_df.isna().sum()
    all_nan_cols = nan_counts[nan_counts == len(feature_df)].index.tolist()
    if len(all_nan_cols) == feature_df.shape[1]:
        raise ValueError("All features are entirely NaN")

    if "amount" in feature_df.columns and "TransactionAmt" in feature_df.columns:
        pass

    logger.info("Feature validation passed")


def filter_valid_features(
    X_train: pd.DataFrame,
    X_val: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str], List[str]]:
    """
    Remove features with 100%% missing values in X_train.

    Args:
        X_train: Training feature dataframe
        X_val: Validation feature dataframe

    Returns:
        Tuple of (filtered_X_train, filtered_X_val, numeric_cols, categorical_cols)
    """
    logger.info("Filtering features with 100%% missing values in training data")

    all_cols = X_train.columns.tolist()
    missing_counts = X_train.isna().sum()
    all_missing = missing_counts[missing_counts == len(X_train)].index.tolist()

    if all_missing:
        logger.info("Excluding %d features with all missing values: %s", len(all_missing), all_missing)

    valid_cols = [col for col in all_cols if col not in all_missing]
    excluded_cols = all_missing

    numeric_cols = [col for col in valid_cols if X_train[col].dtype in [np.float32, np.float64, np.int32, np.int64]]
    categorical_cols = [col for col in valid_cols if X_train[col].dtype.name in ["category", "object"]]

    logger.info("Features after filtering: %d (excluded %d)", len(valid_cols), len(excluded_cols))

    X_train_filtered = X_train[valid_cols]
    X_val_filtered = X_val[valid_cols]

    return X_train_filtered, X_val_filtered, numeric_cols, categorical_cols, excluded_cols


def temporal_split(
    df: pd.DataFrame,
    target: Optional[pd.Series] = None,
    test_size: float = 0.2,
) -> Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.Series], Optional[pd.Series]]:
    """
    Perform temporal train/validation split based on TransactionDT.

    Args:
        df: Feature dataframe
        target: Optional target series
        test_size: Fraction of data for validation

    Returns:
        Tuple of (X_train, X_val, y_train, y_val)
    """
    logger.info("Performing temporal split (test_size=%.2f)", test_size)

    if "transaction_time" not in df.columns:
        raise ValueError("transaction_time column required for temporal split")

    sort_idx = df["transaction_time"].argsort()
    sorted_df = df.iloc[sort_idx].reset_index(drop=True)

    if target is not None:
        sorted_target = target.iloc[sort_idx].reset_index(drop=True)
    else:
        sorted_target = None

    n = len(sorted_df)
    split_idx = int(n * (1 - test_size))

    X_train = sorted_df.iloc[:split_idx].copy()
    X_val = sorted_df.iloc[split_idx:].copy()

    if sorted_target is not None:
        y_train = sorted_target.iloc[:split_idx].copy()
        y_val = sorted_target.iloc[split_idx:].copy()
    else:
        y_train = None
        y_val = None

    logger.info(
        "Temporal split: %d training rows, %d validation rows",
        len(X_train),
        len(X_val),
    )

    if len(X_train) == 0 or len(X_val) == 0:
        raise ValueError("Temporal split resulted in empty train or validation set")

    if y_train is not None and len(y_train) > 0:
        train_min_time = X_train["transaction_time"].min()
        train_max_time = X_train["transaction_time"].max()
        val_min_time = X_val["transaction_time"].min()
        val_max_time = X_val["transaction_time"].max()

        if val_min_time < train_max_time:
            raise ValueError(
                f"Temporal split violated: val_min_time ({val_min_time}) < train_max_time ({train_max_time})"
            )

        logger.info(
            "Train time range: [%.2f, %.2f], Val time range: [%.2f, %.2f]",
            train_min_time,
            train_max_time,
            val_min_time,
            val_max_time,
        )

    return X_train, X_val, y_train, y_val


def build_preprocessor(
    numeric_features: List[str],
    categorical_features: List[str],
) -> Any:
    """
    Build sklearn preprocessing pipeline.

    Args:
        numeric_features: List of numeric feature names
        categorical_features: List of categorical feature names

    Returns:
        Fitted ColumnTransformer
    """
    logger.info("Building preprocessor")
    logger.info("Numeric features: %d", len(numeric_features))
    logger.info("Categorical features: %d", len(categorical_features))

    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OrdinalEncoder

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
        ]
    )

    transformers = []
    if numeric_features:
        transformers.append(("num", numeric_transformer, numeric_features))
    if categorical_features:
        transformers.append(("cat", categorical_transformer, categorical_features))

    if not transformers:
        raise ValueError("No features to preprocess")

    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder="drop",
    )

    return preprocessor


def save_artifacts(
    preprocessor: Any,
    feature_df: pd.DataFrame,
    X_train: pd.DataFrame,
    numeric_features: List[str],
    categorical_features: List[str],
    target_dist: Dict[str, int],
    temporal_info: Dict[str, Any],
    excluded_cols: Optional[List[str]] = None,
) -> None:
    """
    Save preprocessing artifacts and reports.

    Args:
        preprocessor: Fitted preprocessor
        feature_df: Original feature dataframe
        X_train: Training portion (after temporal split and filtering)
        numeric_features: List of numeric feature names
        categorical_features: List of categorical feature names
        target_dist: Target distribution
        temporal_info: Temporal split information
        excluded_cols: Columns excluded due to 100%% missing values
    """
    import joblib

    preprocessor_path = ML_ARTIFACTS_DIR / "preprocessor_ieee_cis_v1.joblib"
    joblib.dump(preprocessor, preprocessor_path)
    logger.info("Saved preprocessor to: %s", preprocessor_path)

    excluded_cols = excluded_cols or []
    active_cols = [col for col in X_train.columns if col not in excluded_cols]

    feature_profile: Dict[str, Any] = {"features": []}

    for col in feature_df.columns:
        col_data_full = feature_df[col]
        missing_pct_full = float(col_data_full.isna().mean() * 100)
        unique_count_full = int(col_data_full.nunique())

        if col in X_train.columns:
            col_data = X_train[col]
            missing_pct = float(col_data.isna().mean() * 100)
            unique_count = int(col_data.nunique())

            if col in numeric_features:
                dtype = "numeric"
                variance = float(col_data.var()) if len(col_data.dropna()) > 1 else None
                is_constant = unique_count <= 1
            else:
                dtype = "categorical"
                variance = None
                is_constant = unique_count <= 1

            if missing_pct == 100 or col in excluded_cols:
                status = "EXCLUDED"
            elif is_constant:
                status = "EXCLUDED"
            else:
                status = "ACTIVE"
        else:
            missing_pct = missing_pct_full
            unique_count = unique_count_full
            if col in numeric_features:
                dtype = "numeric"
            else:
                dtype = "categorical"
            variance = None
            is_constant = True
            status = "EXCLUDED"

        feature_profile["features"].append({
            "name": col,
            "dtype": dtype,
            "missing_percentage": missing_pct,
            "missing_percentage_full": missing_pct_full,
            "unique_count": unique_count,
            "unique_count_full": unique_count_full,
            "variance": variance,
            "is_constant": is_constant,
            "status": status,
        })

    feature_profile_path = ML_REPORTS_DIR / "ieee_cis_feature_profile.json"
    with open(feature_profile_path, "w") as f:
        json.dump(feature_profile, f, indent=2)
    logger.info("Saved feature profile to: %s", feature_profile_path)

    data_profile = {
        "dataset": "ieee_cis",
        "transaction_rows": int(temporal_info.get("transaction_rows", 0)),
        "identity_rows": int(temporal_info.get("identity_rows", 0)),
        "merged_rows": int(temporal_info.get("merged_rows", 0)),
        "feature_count": int(feature_df.shape[1]),
        "active_feature_count": len([f for f in feature_profile["features"] if f["status"] == "ACTIVE"]),
        "train_rows": int(temporal_info.get("train_rows", 0)),
        "validation_rows": int(temporal_info.get("validation_rows", 0)),
        "target_name": "isFraud",
        "target_distribution": target_dist,
        "temporal_split": "80/20 temporal by TransactionDT",
        "minimum_transaction_dt": float(temporal_info.get("min_dt", 0)),
        "maximum_transaction_dt": float(temporal_info.get("max_dt", 0)),
    }

    data_profile_path = ML_REPORTS_DIR / "data_profile.json"
    with open(data_profile_path, "w") as f:
        json.dump(data_profile, f, indent=2)
    logger.info("Saved data profile to: %s", data_profile_path)

    final_schema = {
        "version": "1.0",
        "dataset": "ieee_cis",
        "target": "isFraud",
        "excluded_columns": ["TransactionID", "isFraud"] + excluded_cols,
        "excluded_due_to_missing": excluded_cols,
        "active_features": [f["name"] for f in feature_profile["features"] if f["status"] == "ACTIVE"],
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "preprocessor_artifact": str(preprocessor_path),
        "temporal_split_information": {
            "strategy": "temporal 80/20",
            "train_rows": int(temporal_info.get("train_rows", 0)),
            "validation_rows": int(temporal_info.get("validation_rows", 0)),
        },
    }

    final_schema_path = ML_REPORTS_DIR / "final_feature_schema.json"
    with open(final_schema_path, "w") as f:
        json.dump(final_schema, f, indent=2)
    logger.info("Saved final feature schema to: %s", final_schema_path)


def run_test_mode() -> None:
    """Run feature engineering in test mode with a small sample."""
    print("MODE: TEST")

    ensure_directories()

    logger.info("Running test mode with sample size: %d", TEST_SAMPLE_SIZE)

    merged_df, original_count = load_ieee_cis_data(
        TRAIN_TRANSACTION_PATH,
        TRAIN_IDENTITY_PATH,
        sample_size=TEST_SAMPLE_SIZE,
    )

    print(f"Transaction rows loaded: {TEST_SAMPLE_SIZE}")
    print(f"Identity rows loaded: {len(merged_df) - TEST_SAMPLE_SIZE}")
    print(f"Merged rows: {len(merged_df)}")

    if "isFraud" not in merged_df.columns:
        raise ValueError("isFraud column not found in training data")

    target = merged_df["isFraud"]

    feature_df = build_ieee_cis_features(merged_df)
    validate_features(feature_df, target)

    print(f"Number of source columns: {len(merged_df.columns)}")
    print(f"Number of engineered features: {len(feature_df.columns)}")

    print("\nFeature names:")
    for i, col in enumerate(feature_df.columns):
        print(f"  {i+1}. {col}")

    print("\nSample feature values (first 5 rows):")
    sample_display = feature_df.head(5).copy()
    for col in sample_display.columns:
        if sample_display[col].dtype == "float32" or sample_display[col].dtype == "float64":
            sample_display[col] = sample_display[col].round(4)
    print(sample_display.to_string())

    numeric_cols = feature_df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = feature_df.select_dtypes(include=["category", "object"]).columns.tolist()

    print(f"\nNumeric features: {len(numeric_cols)}")
    print(f"Categorical features: {len(categorical_cols)}")

    if len(numeric_cols) > 0:
        sample_variance = feature_df[numeric_cols].var()
        non_constant = sample_variance[sample_variance > 0]
        print(f"Non-constant numeric features: {len(non_constant)}")
        if len(non_constant) == 0:
            raise ValueError("All numeric features are constant in test sample")

    X_train, X_val, y_train, y_val = temporal_split(feature_df, target, test_size=0.2)

    X_train, X_val, numeric_cols, categorical_cols, excluded_from_filter = filter_valid_features(X_train, X_val)

    print(f"\nTraining rows: {len(X_train)}")
    print(f"Validation rows: {len(X_val)}")
    print(f"X_train shape: {X_train.shape}")
    print(f"X_validation shape: {X_val.shape}")

    if y_train is not None:
        print(f"y_train distribution: {dict(y_train.value_counts())}")
    if y_val is not None:
        print(f"y_validation distribution: {dict(y_val.value_counts())}")

    preprocessor = build_preprocessor(numeric_cols, categorical_cols)
    preprocessor.fit(X_train)

    X_train_transformed = preprocessor.transform(X_train)
    logger.info("Test mode preprocessor fit and transform successful")

    print("\nTest mode validation passed - all checks successful")


def run_full_mode() -> None:
    """Run feature engineering on the complete dataset."""
    print("MODE: FULL")

    ensure_directories()

    logger.info("Running full mode - loading complete dataset")

    merged_df, original_count = load_ieee_cis_data(
        TRAIN_TRANSACTION_PATH,
        TRAIN_IDENTITY_PATH,
        sample_size=None,
    )

    print(f"Transaction rows loaded: {original_count}")
    print(f"Identity rows loaded: {len(merged_df) - original_count}")
    print(f"Merged rows: {len(merged_df)}")

    if "isFraud" not in merged_df.columns:
        raise ValueError("isFraud column not found in training data")

    target = merged_df["isFraud"]

    logger.info("Building features for full dataset")
    feature_df = build_ieee_cis_features(merged_df)
    validate_features(feature_df, target)

    print(f"\nNumber of engineered features: {len(feature_df.columns)}")

    numeric_cols = feature_df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = feature_df.select_dtypes(include=["category", "object"]).columns.tolist()

    print(f"Numeric features: {len(numeric_cols)}")
    print(f"Categorical features: {len(categorical_cols)}")

    logger.info("Performing temporal split")
    X_train, X_val, y_train, y_val = temporal_split(feature_df, target, test_size=0.2)

    X_train, X_val, numeric_cols, categorical_cols, excluded_from_filter = filter_valid_features(X_train, X_val)

    print(f"\nTraining rows: {len(X_train)}")
    print(f"Validation rows: {len(X_val)}")
    print(f"X_train shape: {X_train.shape}")
    print(f"X_validation shape: {X_val.shape}")

    if y_train is not None:
        train_dist = dict(y_train.value_counts())
        print(f"y_train distribution: {train_dist}")
    if y_val is not None:
        val_dist = dict(y_val.value_counts())
        print(f"y_validation distribution: {val_dist}")

    logger.info("Building and fitting preprocessor")
    preprocessor = build_preprocessor(numeric_cols, categorical_cols)

    logger.info("Fitting preprocessor on training data only")
    preprocessor.fit(X_train)

    logger.info("Transforming training data")
    X_train_transformed = preprocessor.transform(X_train)
    logger.info("Transforming validation data")
    X_val_transformed = preprocessor.transform(X_val)

    logger.info("Preprocessing complete - validating transforms")
    if X_train_transformed.shape[0] != X_train.shape[0]:
        raise ValueError(f"X_train transform row mismatch: {X_train_transformed.shape[0]} vs {X_train.shape[0]}")
    if X_val_transformed.shape[0] != X_val.shape[0]:
        raise ValueError(f"X_val transform row mismatch: {X_val_transformed.shape[0]} vs {X_val.shape[0]}")

    import joblib

    preprocessor_path = ML_ARTIFACTS_DIR / "preprocessor_ieee_cis_v1.joblib"
    joblib.dump(preprocessor, preprocessor_path)
    logger.info("Saved preprocessor to: %s", preprocessor_path)

    logger.info("Testing preprocessor reload")
    reload_path = ML_ARTIFACTS_DIR / "preprocessor_ieee_cis_v1.joblib"
    reloaded_preprocessor = joblib.load(reload_path)
    X_val_reloaded = reloaded_preprocessor.transform(X_val)

    if not np.allclose(X_val_transformed, X_val_reloaded):
        raise ValueError("Reloaded preprocessor produces different results")

    temporal_info = {
        "transaction_rows": original_count,
        "identity_rows": len(merged_df) - original_count,
        "merged_rows": len(merged_df),
        "train_rows": len(X_train),
        "validation_rows": len(X_val),
        "min_dt": float(X_train["transaction_time"].min()) if "transaction_time" in X_train.columns else 0,
        "max_dt": float(X_val["transaction_time"].max()) if "transaction_time" in X_val.columns else 0,
    }

    target_dist = {}
    if y_train is not None:
        target_dist["train_legitimate"] = int((y_train == 0).sum())
        target_dist["train_fraud"] = int((y_train == 1).sum())
    if y_val is not None:
        target_dist["val_legitimate"] = int((y_val == 0).sum())
        target_dist["val_fraud"] = int((y_val == 1).sum())

    save_artifacts(
        preprocessor,
        feature_df,
        X_train,
        numeric_cols,
        categorical_cols,
        target_dist,
        temporal_info,
        excluded_from_filter,
    )

    print("\nFull mode completed successfully")
    print(f"Preprocessor artifact: {ML_ARTIFACTS_DIR / 'preprocessor_ieee_cis_v1.joblib'}")
    print(f"Data profile: {ML_REPORTS_DIR / 'data_profile.json'}")
    print(f"Feature profile: {ML_REPORTS_DIR / 'ieee_cis_feature_profile.json'}")
    print(f"Final schema: {ML_REPORTS_DIR / 'final_feature_schema.json'}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="IEEE-CIS Fraud Detection Feature Engineering Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m ml.scripts.ieee_cis_feature_engineering --help
  python -m ml.scripts.ieee_cis_feature_engineering --test
  python -m ml.scripts.ieee_cis_feature_engineering --full
        """,
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run feature engineering on a small sample (test mode)",
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="Run feature engineering on the complete dataset (full mode)",
    )

    args = parser.parse_args()

    if not args.test and not args.full:
        parser.print_help()
        sys.exit(0)

    if args.test:
        run_test_mode()
    elif args.full:
        run_full_mode()


if __name__ == "__main__":
    main()
