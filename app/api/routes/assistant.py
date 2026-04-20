from fastapi import APIRouter, HTTPException, Depends
from app.api.deps import get_current_user_optional
from app.schemas.assistant_schema import ChatRequest, ChatResponse
from app.services.assistant_service import chat_completion_with_context

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest, current_user=Depends(get_current_user_optional)):
    try:
        user_id = str(current_user.get("_id")) if current_user else None
        return await chat_completion_with_context(
            messages=[m.dict() for m in payload.messages],
            user_id=user_id,
            model=payload.model,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
