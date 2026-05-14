import json
import os
from pathlib import Path
from typing import List, Dict, Any

# Re-export the .pkl-based model functions from the ml package
from app.ml.model_loader import get_model
from app.ml.predictor import predict


def _model_file_path() -> Path:
    base = Path(__file__).resolve().parents[1]
    models_dir = base / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir / "ml_model.json"


def _atomic_write(path: Path, data: Dict[str, Any]):
    tmp = path.with_suffix('.tmp')
    with tmp.open('w', encoding='utf-8') as f:
        json.dump(data, f)
    tmp.replace(path)


def train_model(
    training_data: List[Dict[str, float]],
    feature_names: List[str],
    target_key: str = 'target',
    epochs: int = 500,
    lr: float = 0.01,
) -> Dict[str, Any]:
    """Train a simple linear model using batch gradient descent and persist it.

    This implementation uses pure Python to avoid heavy dependencies and
    provides a predictable, auditable model for initial predictions.
    """
    if not training_data:
        raise ValueError('training_data must not be empty')

    n_features = len(feature_names)

    # Initialize weights and bias
    weights = [0.0] * n_features
    bias = 0.0

    m = float(len(training_data))

    for _ in range(max(1, int(epochs))):
        # compute predictions and gradients
        preds = []
        for row in training_data:
            x = [float(row.get(fn, 0.0)) for fn in feature_names]
            y = float(row.get(target_key, 0.0))
            pred = bias + sum(w * xi for w, xi in zip(weights, x))
            preds.append((x, y, pred))

        # gradients
        grad_w = [0.0] * n_features
        grad_b = 0.0
        for x, y, pred in preds:
            err = (y - pred)
            for j in range(n_features):
                grad_w[j] += (-2.0 / m) * x[j] * err
            grad_b += (-2.0 / m) * err

        # update
        for j in range(n_features):
            weights[j] -= lr * grad_w[j]
        bias -= lr * grad_b

    model = {
        "feature_names": feature_names,
        "weights": weights,
        "bias": bias,
        "meta": {"trained_on": len(training_data), "epochs": int(epochs)}
    }

    # Persist model safely
    path = _model_file_path()
    _atomic_write(path, model)
    return model


# get_model and predict are now provided by app.ml (see imports above).
# They use the trained carbon_model.pkl via model_loader + predictor.
