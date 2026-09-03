import os
import pickle
import hashlib
from datetime import datetime
from typing import Optional, List, Tuple
from dataclasses import dataclass

import numpy as np


@dataclass
class ModelArtifact:
    version: str
    algorithm: str
    model_path: str
    feature_names: List[str]
    metrics: dict
    created_at: datetime
    is_active: bool = False


class ModelRegistry:
    _registry: dict = {}
    _artifacts_dir: str = "ml/artifacts"

    @classmethod
    def _ensure_dir(cls):
        os.makedirs(cls._artifacts_dir, exist_ok=True)

    @classmethod
    def register(cls, artifact: ModelArtifact) -> str:
        cls._ensure_dir()
        cls._registry[artifact.version] = artifact
        return artifact.version

    @classmethod
    def get(cls, version: str) -> Optional[ModelArtifact]:
        return cls._registry.get(version)

    @classmethod
    def get_active(cls) -> Optional[ModelArtifact]:
        for artifact in cls._registry.values():
            if artifact.is_active:
                return artifact
        return None

    @classmethod
    def list_versions(cls) -> List[str]:
        return list(cls._registry.keys())

    @classmethod
    def set_active(cls, version: str) -> bool:
        if version not in cls._registry:
            return False
        for v, art in cls._registry.items():
            art.is_active = (v == version)
        return True

    @classmethod
    def save_model(cls, version: str, model, metrics: dict, feature_names: List[str], algorithm: str) -> str:
        cls._ensure_dir()
        safe_version = version.replace("/", "_").replace("\\", "_")
        model_path = os.path.join(cls._artifacts_dir, f"{safe_version}.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        artifact = ModelArtifact(
            version=version,
            algorithm=algorithm,
            model_path=model_path,
            feature_names=feature_names,
            metrics=metrics,
            created_at=datetime.now(),
            is_active=False,
        )
        cls.register(artifact)
        return version

    @classmethod
    def load_model(cls, version: str):
        artifact = cls.get(version)
        if not artifact:
            return None
        if not os.path.exists(artifact.model_path):
            return None
        with open(artifact.model_path, "rb") as f:
            return pickle.load(f)

    @classmethod
    def get_metrics_hash(cls, metrics: dict) -> str:
        metric_str = "_".join(f"{k}={v:.4f}" for k, v in sorted(metrics.items()))
        return hashlib.md5(metric_str.encode()).hexdigest()[:8]


class BaseModel:
    def predict(self, X):
        raise NotImplementedError

    def predict_proba(self, X):
        raise NotImplementedError

    def get_version(self) -> str:
        raise NotImplementedError


class XGBoostModel(BaseModel):
    def __init__(self, model, feature_names: List[str], version: str):
        self._model = model
        self._feature_names = feature_names
        self._version = version

    def predict(self, X) -> np.ndarray:
        return self._model.predict(X)

    def predict_proba(self, X) -> np.ndarray:
        proba = self._model.predict_proba(X)
        if proba.shape[1] == 2:
            return proba[:, 1]
        return proba

    def get_version(self) -> str:
        return self._version

    def get_feature_importance(self) -> dict:
        if hasattr(self._model, "feature_importances_"):
            importances = self._model.feature_importances_
            return {name: float(imp) for name, imp in zip(self._feature_names, importances)}
        return {}


class MockModel(BaseModel):
    def __init__(self, version: str = "mock-v1"):
        self._version = version

    def predict(self, X) -> np.ndarray:
        return np.zeros(len(X))

    def predict_proba(self, X) -> np.ndarray:
        return np.zeros(len(X))

    def get_version(self) -> str:
        return self._version


_MODEL_CACHE: dict = {}


def get_model(version: Optional[str] = None) -> BaseModel:
    if version:
        model = ModelRegistry.load_model(version)
        if model:
            return model
    active = ModelRegistry.get_active()
    if active:
        model = ModelRegistry.load_model(active.version)
        if model:
            return model
    return MockModel()
