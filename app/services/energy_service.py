from app.models.energy_model import EnergyModel
from app.schemas.energy_schema import EnergyCreate, EnergyUpdate

async def log_energy(user_id: str, energy_in: EnergyCreate):
    energy_dict = energy_in.model_dump()
    energy_dict["user_id"] = user_id
    return await EnergyModel.create(energy_dict)

async def get_user_energy_logs(user_id: str):
    return await EnergyModel.find_by_user_id(user_id)

async def update_energy_log(record_id: str, update_data: EnergyUpdate, user_id: str = None):
    return await EnergyModel.update(record_id, update_data.model_dump(exclude_unset=True), user_id=user_id)

async def delete_energy_log(record_id: str, user_id: str = None):
    return await EnergyModel.delete(record_id, user_id=user_id)
