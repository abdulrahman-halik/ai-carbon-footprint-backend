from bson import ObjectId
from app.db import mongodb
from app.models.user_model import UserModel
from app.models.emission_model import EmissionModel
from app.models.energy_model import EnergyModel
from app.models.water_model import WaterModel
from app.models.goal_model import GoalModel
from app.schemas.user_schema import OnboardingComplete, ProfileUpdate


async def start_onboarding(user_id: str):
    user = await UserModel.find_by_id(user_id)
    if not user:
        return None
    update_data = {
        "onboarding_completed": False,
        "profile": user.get("profile", {})
    }
    return await UserModel.update(user_id, update_data)


async def complete_onboarding(user_id: str, onboarding_data: OnboardingComplete):
    update_data = {
        "onboarding_completed": True,
        "profile": onboarding_data.profile
    }
    return await UserModel.update(user_id, update_data)


async def get_user_profile(user_id: str):
    user = await UserModel.find_by_id(user_id)
    if not user:
        return None
    return user.get("profile", {})


async def update_user_profile(user_id: str, profile_data: ProfileUpdate):
    update_data = {}
    if profile_data.full_name is not None:
        update_data["full_name"] = profile_data.full_name
    if profile_data.profile is not None:
        update_data["profile"] = profile_data.profile
    return await UserModel.update(user_id, update_data)


async def delete_user_account(user_id: str) -> bool:
    """Fix #13: Cascade-delete all records owned by the user before removing the user."""
    if not ObjectId.is_valid(user_id):
        return False
    # Remove all associated data first
    await EmissionModel.delete_by_user_id(user_id)
    await EnergyModel.delete_by_user_id(user_id)
    await WaterModel.delete_by_user_id(user_id)
    await GoalModel.delete_by_user_id(user_id)
    # Finally remove the user document itself
    return await UserModel.delete(user_id)
