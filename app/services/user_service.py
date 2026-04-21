from app.models.user_model import UserModel
from app.schemas.user_schema import OnboardingComplete, ProfileUpdate

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

async def update_user_profile(user_id: str, profile_data: ProfileUpdate):
    update_data = {}
    if profile_data.full_name is not None:
        update_data["full_name"] = profile_data.full_name
    if profile_data.profile is not None:
        # Merge or replace profile? userService.js sends the whole profile object
        update_data["profile"] = profile_data.profile
    
    return await UserModel.update(user_id, update_data)

async def delete_user_account(user_id: str):
    # This would need a delete method in UserModel if it doesn't exist
    # Let's check UserModel again.
    from app.db import mongodb
    from bson import ObjectId
    result = mongodb.db.users.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0
