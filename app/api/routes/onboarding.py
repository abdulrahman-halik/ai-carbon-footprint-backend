from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user
from app.schemas.user_schema import UserOut, OnboardingComplete
from app.services.user_service import start_onboarding, complete_onboarding

router = APIRouter()

@router.post("/start", response_model=UserOut)
async def onboarding_start(current_user: dict = Depends(get_current_user)):
    user = await start_onboarding(str(current_user["_id"]))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/complete", response_model=UserOut)
async def onboarding_complete(
    onboarding_data: OnboardingComplete,
    current_user: dict = Depends(get_current_user)
):
    user = await complete_onboarding(str(current_user["_id"]), onboarding_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
