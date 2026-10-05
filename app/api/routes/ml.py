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

@router.get("/base-features")
async def get_base_features(current_user: dict = Depends(get_current_user)):
    from app.models.emission_model import EmissionModel
    from app.models.energy_model import EnergyModel
    
    user_id = str(current_user["_id"])
    
    # Defaults
    features = {
        "Daily_Travel_km": 20.0,
        "Electricity_Usage_kWh_per_month": 300.0,
        "Meat_Consumption_per_week": 5.0
    }
    
    emissions = await EmissionModel.find_by_user_id(user_id)
    transport_logs = [log for log in emissions if log.get("category") == "Transport" and log.get("distance") is not None]
    if transport_logs:
        total_dist = sum(float(log["distance"]) for log in transport_logs)
        features["Daily_Travel_km"] = total_dist / len(transport_logs)
        
    food_logs = [log for log in emissions if log.get("category") == "Food"]
    if food_logs:
        diet_map = {"meat-heavy": 14.0, "omnivore": 7.0, "vegetarian": 2.0, "vegan": 0.0}
        latest_diet = food_logs[0].get("sub_category", "omnivore") 
        features["Meat_Consumption_per_week"] = diet_map.get(latest_diet, 5.0)

    energy_logs = await EnergyModel.find_by_user_id(user_id)
    if energy_logs:
        total_energy = sum(float(log.get("value", 0)) for log in energy_logs)
        features["Electricity_Usage_kWh_per_month"] = total_energy / len(energy_logs)
        
    return features
