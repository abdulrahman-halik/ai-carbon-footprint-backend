"""
predictor.py — Use the trained brain to answer: predict carbon footprint.

This is the single entry-point used by the rest of the application.
It wires model_loader + preprocess together and returns a plain float.
"""

from typing import Dict

from app.ml.model_loader import get_model
from app.ml.preprocess import prepare_input


def predict(features: Dict[str, float]) -> float:
    """Predict the carbon footprint (kg CO₂e) for the given activity features.

    Args:
        features: Dict mapping feature names to numeric values.
                  See preprocess.FEATURE_ORDER for the full list.
                  Unknown keys are ignored; missing keys default to 0.0.

    Returns:
        Predicted carbon footprint as a float (kg CO₂e).

    Raises:
        FileNotFoundError: If the model .pkl file has not been placed on disk.
        RuntimeError: If the model cannot be deserialized.
        ValueError: If `features` is invalid.
    """
    model = get_model()
    X = prepare_input(features)
    result = model.predict(X)
    # result is typically a 1-D array; extract the scalar
    return float(result[0])
