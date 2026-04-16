from app.models.water_model import WaterModel
from app.schemas.water_schema import WaterCreate, WaterUpdate

async def log_water_usage(user_id: str, water_in: WaterCreate):
    water_dict = water_in.model_dump()
    water_dict["user_id"] = user_id
    return await WaterModel.create(water_dict)

async def get_user_water_logs(user_id: str):
    return await WaterModel.find_by_user_id(user_id)

async def update_water_log(record_id: str, update_data: WaterUpdate):
    return await WaterModel.update(record_id, update_data.model_dump(exclude_unset=True))

async def delete_water_log(record_id: str):
    return await WaterModel.delete(record_id)
