from fastapi import APIRouter, Depends, HTTPException
from app.schemas.ml_schema import PredictRequest, PredictResponse
from app.services.ml_service import predict, get_model
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
async def predict_endpoint(
    payload: PredictRequest,
    current_user: dict = Depends(get_current_user),  # Fix #7: endpoint now requires auth
):
    if not payload.features:
        raise HTTPException(status_code=400, detail="features must be provided")
    try:
        value = predict(payload.features)
        return {"prediction": value}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



