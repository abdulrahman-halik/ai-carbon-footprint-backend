from fastapi import APIRouter, Depends
from app.schemas.user_schema import UserOut, ProfileUpdate
from app.api.deps import get_current_user
from app.services.user_service import update_user_profile, delete_user_account

router = APIRouter()

@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserOut)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    return await update_user_profile(str(current_user["_id"]), profile_data)

@router.delete("/me")
async def delete_me(current_user: dict = Depends(get_current_user)):
    success = await delete_user_account(str(current_user["_id"]))
    if not success:
        return {"message": "User not found or already deleted"}
    return {"message": "Account deleted successfully"}
