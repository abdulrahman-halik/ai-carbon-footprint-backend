from pydantic import BaseModel
from typing import Dict, List, Any


class PredictRequest(BaseModel):
    features: Dict[str, float]


class PredictResponse(BaseModel):
    prediction: float


class TrainRequest(BaseModel):
    data: List[Dict[str, Any]]
    feature_names: List[str]
    target_key: str = 'target'
    epochs: int = 500
    lr: float = 0.01
