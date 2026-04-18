from fastapi import APIRouter, Depends, HTTPException
from app.schemas.ml_schema import PredictRequest, PredictResponse, TrainRequest
from app.services.ml_service import train_model, predict, get_model
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
async def predict_endpoint(payload: PredictRequest):
    # Validate input sizes lightly (no heavy computation here)
    if not payload.features:
        raise HTTPException(status_code=400, detail="features must be provided")
    try:
        value = predict(payload.features)
        return {"prediction": value}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/train")
async def train_endpoint(payload: TrainRequest, current_user: dict = Depends(get_current_user)):
    # Only authenticated users may trigger training in this simple setup
    try:
        model = train_model(payload.data, payload.feature_names, payload.target_key, epochs=payload.epochs, lr=payload.lr)
        return {"message": "Model trained", "meta": model.get('meta', {})}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
