from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.services.dashboard_service import get_dashboard_summary

router = APIRouter()

@router.get("/summary")
async def dashboard_summary(current_user: dict = Depends(get_current_user)):
    return await get_dashboard_summary(str(current_user["_id"]))
