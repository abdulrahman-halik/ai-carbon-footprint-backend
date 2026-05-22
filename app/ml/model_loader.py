"""
model_loader.py — Load the trained .pkl brain once and cache it in memory.

Uses joblib (the standard serialiser for scikit-learn models) instead of
plain pickle to handle cross-version compatibility warnings gracefully.
"""

import warnings
from pathlib import Path
from typing import Any

import joblib

# Absolute path to the trained model file
_MODEL_PATH = Path(__file__).resolve().parent.parent / "artifacts" / "carbon_model.pkl"

# Module-level singleton — model is loaded only once per process
_cached_model: Any = None


def get_model() -> Any:
    """Return the loaded sklearn model, loading from disk on first call.

    Returns:
        A fitted sklearn estimator (RandomForestRegressor).

    Raises:
        FileNotFoundError: If the .pkl file does not exist on disk.
        RuntimeError: If the model file cannot be deserialized.
    """
    global _cached_model
    if _cached_model is not None:
        return _cached_model

    if not _MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found at {_MODEL_PATH}. "
            "Please place carbon_model.pkl inside app/artifacts/."
        )

    try:
        with warnings.catch_warnings():
            # Suppress sklearn InconsistentVersionWarning on minor version diffs
            warnings.simplefilter("ignore")
            _cached_model = joblib.load(_MODEL_PATH)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load model from {_MODEL_PATH}: {exc}"
        ) from exc

    return _cached_model
