from typing import Optional
from app.models.user_model import UserModel
from app.schemas.user_schema import OnboardingComplete

async def start_onboarding(user_id: str):
    # Initialize profile if not exists
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
