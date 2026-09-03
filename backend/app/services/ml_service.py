from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

_ML_AVAILABLE = False
_ModelRegistry = None

try:
    from app.ml.models import ModelRegistry
    _ML_AVAILABLE = True
    _ModelRegistry = ModelRegistry
except ImportError:
    logger.warning("ML libraries not available")


def is_ml_available() -> bool:
    return _ML_AVAILABLE


def get_active_model_version() -> Optional[str]:
    if not _ML_AVAILABLE:
        return None
    active = _ModelRegistry.get_active()
    return active.version if active else None


def get_model_info(version: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if not _ML_AVAILABLE:
        return None
    if version:
        art = _ModelRegistry.get(version)
    else:
        art = _ModelRegistry.get_active()
    if not art:
        return None
    return {
        "version": art.version,
        "algorithm": art.algorithm,
        "metrics": art.metrics,
        "feature_names": art.feature_names,
        "created_at": art.created_at.isoformat() if art.created_at else None,
        "is_active": art.is_active,
    }


def list_model_versions() -> List[str]:
    if not _ML_AVAILABLE:
        return []
    return _ModelRegistry.list_versions()


def set_active_model(version: str) -> bool:
    if not _ML_AVAILABLE:
        return False
    return _ModelRegistry.set_active(version)
