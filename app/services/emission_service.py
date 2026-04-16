from typing import List, Optional
from app.models.emission_model import EmissionModel
from app.schemas.emission_schema import EmissionCreate, EmissionUpdate

# Basic emission factors (kg CO2e per unit)
# These should ideally come from a database or config
EMISSION_FACTORS = {
    "Transport": {
        "Petrol Car": 0.17,  # per km
        "Electric Car": 0.05, # per km
        "Bus": 0.03, # per km
        "Train": 0.04, # per km
        "Flight": 0.15, # per km
    },
    "Food": {
        "Meat-heavy": 7.2, # per day
        "Vegetarian": 3.8, # per day
        "Vegan": 2.9, # per day
    },
    "Energy": {
        "Electricity": 0.23, # per kWh
        "Natural Gas": 0.18, # per kWh
    }
}

async def log_emission(user_id: str, emission_in: EmissionCreate):
    emission_dict = emission_in.model_dump()
    emission_dict["user_id"] = user_id
    
    # Optional logic: adjust value based on emission factors if not provided or to validate?
    # For now, we trust the value passed, or provide a way to calculate it.
    
    return await EmissionModel.create(emission_dict)

async def get_user_emissions(user_id: str):
    return await EmissionModel.find_by_user_id(user_id)

async def update_emission(record_id: str, update_data: EmissionUpdate):
    return await EmissionModel.update(record_id, update_data.model_dump(exclude_unset=True))

async def delete_emission(record_id: str):
    return await EmissionModel.delete(record_id)

async def get_emission_stats(user_id: str):
    return await EmissionModel.get_aggregated_stats(user_id)
