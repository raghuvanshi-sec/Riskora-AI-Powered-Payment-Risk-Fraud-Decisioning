"""
Phase 6.5C — IEEE-CIS Model Training and Comparison
====================================================

Train and compare Logistic Regression, Random Forest, and XGBoost
on the IEEE-CIS fraud detection dataset using the preprocessing
artifacts from Phase 6.5B.4.

Usage:
    python -m ml.scripts.ieee_cis_training --help
    python -m ml.scripts.ieee_cis_training --train
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
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

TEST_SAMPLE_SIZE = 5000


@dataclass
class ModelMetrics:
    pr_auc: float
    roc_auc: float
    precision: float
    recall: float
    f1: float
    accuracy: float
    confusion_matrix: List[List[int]]
    training_time: float


@dataclass
class TrainedModel:
    model: Any
    name: str
    metrics: ModelMetrics
    parameters: Dict[str, Any]


def ensure_directories() -> None:
    """Create required output directories."""
    ML_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    ML_REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_ieee_cis_data(
    transaction_path: Path,
    identity_path: Path,
    sample_size: Optional[int] = None,
) -> Tuple[pd.DataFrame, pd.Series, int]:
    """
    Load and merge IEEE-CIS transaction and identity data.

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

    if "isFraud" not in merged_df.columns:
        raise ValueError("isFraud column not found in training data")

    target = merged_df["isFraud"]

    return merged_df, target, original_count


def build_ieee_cis_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build engineered features from IEEE-CIS data.
    Must match Phase 6.5B.4 feature engineering exactly.
    """
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
    """
    Remove features with 100% missing values in X_train.
    Must match Phase 6.5B.4 filtering.
    """
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
    """
    Perform temporal train/validation split based on TransactionDT.
    Must match Phase 6.5B.4 temporal split.
    """
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


def load_preprocessor():
    """Load the fitted preprocessor from Phase 6.5B.4."""
    import joblib

    if not PREPROCESSOR_PATH.exists():
        raise FileNotFoundError(f"Preprocessor not found at {PREPROCESSOR_PATH}. Run Phase 6.5B.4 first.")

    preprocessor = joblib.load(PREPROCESSOR_PATH)
    logger.info("Loaded preprocessor from: %s", PREPROCESSOR_PATH)
    return preprocessor


def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray,
) -> ModelMetrics:
    """Calculate comprehensive metrics for model evaluation."""
    from sklearn.metrics import (
        accuracy_score,
        precision_score,
        recall_score,
        f1_score,
        roc_auc_score,
        confusion_matrix,
        precision_recall_curve,
        auc,
    )

    metrics = ModelMetrics(
        pr_auc=0.0,
        roc_auc=0.0,
        precision=0.0,
        recall=0.0,
        f1=0.0,
        accuracy=0.0,
        confusion_matrix=[[0, 0], [0, 0]],
        training_time=0.0,
    )

    metrics.accuracy = float(accuracy_score(y_true, y_pred))
    metrics.precision = float(precision_score(y_true, y_pred, zero_division=0))
    metrics.recall = float(recall_score(y_true, y_pred, zero_division=0))
    metrics.f1 = float(f1_score(y_true, y_pred, zero_division=0))

    try:
        metrics.roc_auc = float(roc_auc_score(y_true, y_proba))
    except ValueError:
        metrics.roc_auc = 0.0

    try:
        precision_curve, recall_curve, _ = precision_recall_curve(y_true, y_proba)
        metrics.pr_auc = float(auc(recall_curve, precision_curve))
    except ValueError:
        metrics.pr_auc = 0.0

    cm = confusion_matrix(y_true, y_pred)
    metrics.confusion_matrix = cm.tolist()

    return metrics


def train_logistic_regression(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
) -> TrainedModel:
    """Train Logistic Regression model."""
    from sklearn.linear_model import LogisticRegression

    logger.info("Training Logistic Regression...")
    start_time = time.time()

    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        solver="lbfgs",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    training_time = time.time() - start_time

    y_proba = model.predict_proba(X_val)[:, 1]
    y_pred = model.predict(X_val)

    metrics = calculate_metrics(y_val.values, y_pred, y_proba)
    metrics.training_time = training_time

    parameters = {
        "max_iter": 1000,
        "class_weight": "balanced",
        "solver": "lbfgs",
        "random_state": 42,
    }

    logger.info(
        "Logistic Regression trained in %.2fs - PR-AUC: %.4f, ROC-AUC: %.4f",
        training_time,
        metrics.pr_auc,
        metrics.roc_auc,
    )

    return TrainedModel(
        model=model,
        name="logistic_regression",
        metrics=metrics,
        parameters=parameters,
    )


def train_random_forest(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
) -> TrainedModel:
    """Train Random Forest model."""
    from sklearn.ensemble import RandomForestClassifier

    logger.info("Training Random Forest...")
    start_time = time.time()

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=10,
        min_samples_leaf=5,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    training_time = time.time() - start_time

    y_proba = model.predict_proba(X_val)[:, 1]
    y_pred = model.predict(X_val)

    metrics = calculate_metrics(y_val.values, y_pred, y_proba)
    metrics.training_time = training_time

    parameters = {
        "n_estimators": 200,
        "max_depth": 15,
        "min_samples_split": 10,
        "min_samples_leaf": 5,
        "class_weight": "balanced_subsample",
        "random_state": 42,
    }

    logger.info(
        "Random Forest trained in %.2fs - PR-AUC: %.4f, ROC-AUC: %.4f",
        training_time,
        metrics.pr_auc,
        metrics.roc_auc,
    )

    return TrainedModel(
        model=model,
        name="random_forest",
        metrics=metrics,
        parameters=parameters,
    )


def train_xgboost(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
) -> TrainedModel:
    """Train XGBoost model."""
    import xgboost as xgb

    logger.info("Training XGBoost...")

    neg_count = int((y_train == 0).sum())
    pos_count = int((y_train == 1).sum())
    scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1.0

    logger.info("scale_pos_weight = %d / %d = %.4f", neg_count, pos_count, scale_pos_weight)

    start_time = time.time()

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        n_jobs=-1,
        use_label_encoder=False,
        eval_metric="logloss",
    )

    model.fit(X_train, y_train)

    training_time = time.time() - start_time

    y_proba = model.predict_proba(X_val)[:, 1]
    y_pred = model.predict(X_val)

    metrics = calculate_metrics(y_val.values, y_pred, y_proba)
    metrics.training_time = training_time

    parameters = {
        "n_estimators": 200,
        "max_depth": 6,
        "learning_rate": 0.1,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "scale_pos_weight": scale_pos_weight,
        "random_state": 42,
    }

    logger.info(
        "XGBoost trained in %.2fs - PR-AUC: %.4f, ROC-AUC: %.4f",
        training_time,
        metrics.pr_auc,
        metrics.roc_auc,
    )

    return TrainedModel(
        model=model,
        name="xgboost",
        metrics=metrics,
        parameters=parameters,
    )


def save_model_artifact(
    best_model: TrainedModel,
    preprocessor_version: str,
    feature_schema_version: str,
    selection_metric: str,
) -> Path:
    """Save the best model artifact."""
    import joblib
    from dataclasses import asdict

    artifact = {
        "model": best_model.model,
        "model_name": best_model.name,
        "model_version": "risk_model_v1",
        "preprocessor_version": preprocessor_version,
        "feature_schema_version": feature_schema_version,
        "selection_metric": selection_metric,
        "metrics": asdict(best_model.metrics),
        "parameters": best_model.parameters,
        "created_at": datetime.now().isoformat(),
    }

    artifact_path = ML_ARTIFACTS_DIR / "risk_model_v1.joblib"
    joblib.dump(artifact, artifact_path)
    logger.info("Saved model artifact to: %s", artifact_path)

    return artifact_path


def save_model_comparison_report(
    models: List[TrainedModel],
    selected_model: TrainedModel,
    dataset_info: Dict[str, Any],
    temporal_info: Dict[str, Any],
) -> Path:
    """Save the model comparison report."""
    models_dict = {}
    for tm in models:
        models_dict[tm.name] = {
            "metrics": asdict(tm.metrics),
            "parameters": tm.parameters,
        }

    report = {
        "dataset": dataset_info["dataset"],
        "training_rows": dataset_info["training_rows"],
        "validation_rows": dataset_info["validation_rows"],
        "positive_training": dataset_info["positive_training"],
        "negative_training": dataset_info["negative_training"],
        "positive_validation": dataset_info["positive_validation"],
        "negative_validation": dataset_info["negative_validation"],
        "training_time_range": temporal_info["training_time_range"],
        "validation_time_range": temporal_info["validation_time_range"],
        "models": models_dict,
        "selected_model": selected_model.name,
        "selection_metric": "PR-AUC",
        "selection_reason": f"Highest validation PR-AUC ({selected_model.metrics.pr_auc:.4f}) among all trained models",
    }

    report_path = ML_REPORTS_DIR / "model_comparison.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    logger.info("Saved model comparison report to: %s", report_path)
    return report_path


def verify_leakage(
    X_train: pd.DataFrame,
    X_val: pd.DataFrame,
    y_train: pd.Series,
    y_val: pd.Series,
) -> None:
    """Verify no data leakage occurred."""
    logger.info("Performing leakage checks...")

    if "TransactionID" in X_train.columns:
        raise ValueError("TransactionID found in training features - LEAKAGE DETECTED")

    if "isFraud" in X_train.columns:
        raise ValueError("isFraud found in training features - LEAKAGE DETECTED")

    if X_train.shape[0] == 0 or X_val.shape[0] == 0:
        raise ValueError("Empty train or validation set")

    if y_train.isna().all():
        raise ValueError("All training labels are NaN")

    logger.info("Leakage checks passed")


def print_header():
    """Print phase header."""
    print("=" * 60)
    print("PHASE 6.5C — MODEL TRAINING")
    print("=" * 60)


def print_model_results(model: TrainedModel) -> None:
    """Print model results in standardized format."""
    print(f"\n{model.name.upper().replace('_', ' ')}")
    print("-" * 40)
    print(f"Training time: {model.metrics.training_time:.2f}s")
    print(f"PR-AUC: {model.metrics.pr_auc:.4f}")
    print(f"ROC-AUC: {model.metrics.roc_auc:.4f}")
    print(f"Precision: {model.metrics.precision:.4f}")
    print(f"Recall: {model.metrics.recall:.4f}")
    print(f"F1: {model.metrics.f1:.4f}")
    print(f"Accuracy: {model.metrics.accuracy:.4f}")
    print(f"Confusion Matrix: {model.metrics.confusion_matrix}")


def run_training() -> None:
    """Run the complete training pipeline."""
    print_header()

    ensure_directories()

    logger.info("Loading IEEE-CIS data (full dataset)")
    merged_df, target, original_count = load_ieee_cis_data(
        TRAIN_TRANSACTION_PATH,
        TRAIN_IDENTITY_PATH,
        sample_size=None,
    )

    print(f"\nDataset: IEEE-CIS")
    print(f"Transaction rows loaded: {original_count}")
    print(f"Identity rows loaded: {len(merged_df) - original_count}")
    print(f"Merged rows: {len(merged_df)}")

    logger.info("Building features")
    feature_df = build_ieee_cis_features(merged_df)
    logger.info("Number of engineered features: %d", len(feature_df.columns))

    logger.info("Performing temporal split")
    X_train_raw, X_val_raw, y_train, y_val = temporal_split(feature_df, target, test_size=0.2)

    logger.info("Filtering features with 100%% missing values")
    X_train, X_val, numeric_cols, categorical_cols, excluded_cols = filter_valid_features(
        X_train_raw, X_val_raw
    )

    train_min_dt = float(X_train["transaction_time"].min())
    train_max_dt = float(X_train["transaction_time"].max())
    val_min_dt = float(X_val["transaction_time"].min())
    val_max_dt = float(X_val["transaction_time"].max())

    print(f"\nTraining rows: {len(X_train)}")
    print(f"Validation rows: {len(X_val)}")
    print(f"Training TransactionDT range: [{train_min_dt:.2f}, {train_max_dt:.2f}]")
    print(f"Validation TransactionDT range: [{val_min_dt:.2f}, {val_max_dt:.2f}]")
    print(f"Active features: {len(X_train.columns)}")

    verify_leakage(X_train, X_val, y_train, y_val)

    logger.info("Loading preprocessor from Phase 6.5B.4")
    preprocessor = load_preprocessor()

    logger.info("Transforming training data")
    X_train_transformed = preprocessor.transform(X_train)

    logger.info("Transforming validation data")
    X_val_transformed = preprocessor.transform(X_val)

    logger.info("X_train_transformed shape: %s", X_train_transformed.shape)
    logger.info("X_val_transformed shape: %s", X_val_transformed.shape)

    pos_train = int((y_train == 1).sum())
    neg_train = int((y_train == 0).sum())
    pos_val = int((y_val == 1).sum())
    neg_val = int((y_val == 0).sum())

    print(f"\nPositive training: {pos_train}")
    print(f"Negative training: {neg_train}")
    print(f"Positive validation: {pos_val}")
    print(f"Negative validation: {neg_val}")

    models: List[TrainedModel] = []

    print("\n" + "=" * 60)
    print("LOGISTIC REGRESSION")
    print("=" * 60)
    print("Training...")
    lr_model = train_logistic_regression(X_train_transformed, y_train, X_val_transformed, y_val)
    models.append(lr_model)
    print_model_results(lr_model)

    print("\n" + "=" * 60)
    print("RANDOM FOREST")
    print("=" * 60)
    print("Training...")
    rf_model = train_random_forest(X_train_transformed, y_train, X_val_transformed, y_val)
    models.append(rf_model)
    print_model_results(rf_model)

    print("\n" + "=" * 60)
    print("XGBOOST")
    print("=" * 60)
    print("Training...")
    xgb_model = train_xgboost(X_train_transformed, y_train, X_val_transformed, y_val)
    models.append(xgb_model)
    print_model_results(xgb_model)

    print("\n" + "=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)
    print(f"\n{'Model':<25} {'PR-AUC':>10} {'ROC-AUC':>10} {'Precision':>10} {'Recall':>10} {'F1':>10} {'Accuracy':>10}")
    print("-" * 85)
    for tm in models:
        print(
            f"{tm.name:<25} {tm.metrics.pr_auc:>10.4f} {tm.metrics.roc_auc:>10.4f} "
            f"{tm.metrics.precision:>10.4f} {tm.metrics.recall:>10.4f} "
            f"{tm.metrics.f1:>10.4f} {tm.metrics.accuracy:>10.4f}"
        )

    best_model = max(models, key=lambda m: m.metrics.pr_auc)

    print("\n" + "=" * 60)
    print("SELECTED MODEL")
    print("=" * 60)
    print(f"Model: {best_model.name}")
    print(f"Selection metric: PR-AUC")
    print(f"Reason: Highest validation PR-AUC ({best_model.metrics.pr_auc:.4f}) among all trained models")

    logger.info("Saving best model artifact")
    artifact_path = save_model_artifact(
        best_model,
        preprocessor_version="v1",
        feature_schema_version="v1",
        selection_metric="PR-AUC",
    )

    dataset_info = {
        "dataset": "ieee_cis",
        "training_rows": len(X_train),
        "validation_rows": len(X_val),
        "positive_training": pos_train,
        "negative_training": neg_train,
        "positive_validation": pos_val,
        "negative_validation": neg_val,
    }

    temporal_info = {
        "training_time_range": [train_min_dt, train_max_dt],
        "validation_time_range": [val_min_dt, val_max_dt],
    }

    report_path = save_model_comparison_report(models, best_model, dataset_info, temporal_info)

    print("\n" + "=" * 60)
    print("ARTIFACT VALIDATION")
    print("=" * 60)

    import joblib

    logger.info("Testing model artifact reload")
    reload_path = ML_ARTIFACTS_DIR / "risk_model_v1.joblib"
    reloaded_artifact = joblib.load(reload_path)

    logger.info("Testing prediction with reloaded model")
    reloaded_model = reloaded_artifact["model"]
    X_val_reloaded = preprocessor.transform(X_val)
    reloaded_proba = reloaded_model.predict_proba(X_val_reloaded)[:, 1]

    if not np.all(np.isfinite(reloaded_proba)):
        raise ValueError("Reloaded model produced non-finite predictions")

    print(f"Saved: {artifact_path}")
    print(f"Saved: {report_path}")
    print("Reload test: PASSED")
    print("Prediction test: PASSED")

    print("\n" + "=" * 60)
    print("PHASE 6.5C COMPLETE")
    print("=" * 60)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Phase 6.5C — IEEE-CIS Model Training and Comparison",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--train",
        action="store_true",
        help="Run the complete training pipeline",
    )

    args = parser.parse_args()

    if args.train:
        run_training()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
