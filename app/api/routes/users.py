from fastapi import APIRouter, Depends
from app.schemas.user_schema import UserOut
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
