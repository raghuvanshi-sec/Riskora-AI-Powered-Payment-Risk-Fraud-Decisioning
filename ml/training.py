import os
import logging
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    algorithm: str = "xgboost"
    n_estimators: int = 100
    max_depth: int = 6
    learning_rate: float = 0.1
    subsample: float = 0.8
    colsample_bytree: float = 0.8
    random_state: int = 42
    n_jobs: int = -1


@dataclass
class TrainingResult:
    version: str
    algorithm: str
    metrics: Dict[str, float]
    feature_importance: Dict[str, float]
    config: Dict[str, Any]
    training_samples: int
    test_samples: int


def _train_xgboost(
    X_train, y_train,
    X_test, y_test,
    config: TrainingConfig
) -> Tuple[Any, Dict[str, float], Dict[str, float]]:
    try:
        import xgboost as xgb
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    except ImportError:
        logger.warning("xgboost or sklearn not available, using mock training")
        return None, {}, {}

    model = xgb.XGBClassifier(
        n_estimators=config.n_estimators,
        max_depth=config.max_depth,
        learning_rate=config.learning_rate,
        subsample=config.subsample,
        colsample_bytree=config.colsample_bytree,
        random_state=config.random_state,
        n_jobs=config.n_jobs,
        use_label_encoder=False,
        eval_metric="logloss",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if model.classes_.shape[0] == 2 else np.zeros_like(y_pred)

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
    }
    try:
        metrics["roc_auc"] = float(roc_auc_score(y_test, y_proba))
    except Exception:
        metrics["roc_auc"] = 0.0

    feature_importance = {}
    if hasattr(model, "feature_importances_"):
        from .features import get_feature_names
        for name, imp in zip(get_feature_names(), model.feature_importances_):
            feature_importance[name] = float(imp)

    return model, metrics, feature_importance


def _generate_synthetic_labels(n: int, fraud_rate: float = 0.12, seed: int = 42) -> np.ndarray:
    np.random.seed(seed)
    labels = np.random.binomial(1, fraud_rate, n)
    return labels


def train_model(
    X,
    y,
    config: Optional[TrainingConfig] = None,
    version: str = "ml-v1",
    train_size: float = 0.8,
) -> TrainingResult:
    from .models import ModelRegistry, XGBoostModel
    from .features import get_feature_names

    if config is None:
        config = TrainingConfig()

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=1 - train_size, random_state=config.random_state, stratify=y
    )

    logger.info(f"Training {config.algorithm} model: {len(X_train)} train, {len(X_test)} test samples")

    model, metrics, feature_importance = _train_xgboost(X_train, y_train, X_test, y_test, config)

    if model is not None:
        model = XGBoostModel(model, get_feature_names(), version)
        ModelRegistry.save_model(version, model, metrics, get_feature_names(), config.algorithm)
        ModelRegistry.set_active(version)
        logger.info(f"Model trained and registered as {version}: {metrics}")
    else:
        logger.warning("Model training failed, using mock model")
        mock = MockModel(version) if "MockModel" in dir() else None

    return TrainingResult(
        version=version,
        algorithm=config.algorithm,
        metrics=metrics,
        feature_importance=feature_importance,
        config={
            "n_estimators": config.n_estimators,
            "max_depth": config.max_depth,
            "learning_rate": config.learning_rate,
            "subsample": config.subsample,
            "colsample_bytree": config.colsample_bytree,
        },
        training_samples=len(X_train),
        test_samples=len(X_test),
    )


def train_from_dataset(
    transactions: List[dict],
    labels: Optional[List[int]] = None,
    config: Optional[TrainingConfig] = None,
    version: str = "ml-v1",
) -> TrainingResult:
    from .features import transactions_to_feature_matrix

    X = transactions_to_feature_matrix(transactions)
    y_array = np.array(labels) if labels is not None else None

    if y_array is None:
        logger.warning("No labels provided, generating synthetic labels for development")
        y_array = _generate_synthetic_labels(len(X))

    return train_model(X.values, y_array, config=config, version=version)
