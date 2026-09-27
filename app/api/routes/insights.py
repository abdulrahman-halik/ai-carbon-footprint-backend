from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.deps import get_current_user
from app.services.recommendation_service import search_insights, index_documents

router = APIRouter()


from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str
    parts: str | list[str]
    
class ChatPayload(BaseModel):
    messages: List[ChatMessage]

@router.post("/chat")
async def insights_chat(payload: ChatPayload):
    from app.services.ai_service import chat_with_ai
    try:
        # Convert Pydantic models to dicts expected by Gemini API
        messages_dicts = [ {"role": msg.role, "parts": [msg.parts] if isinstance(msg.parts, str) else msg.parts} for msg in payload.messages ]
        response_text = chat_with_ai(messages_dicts)
        return {"insight": response_text}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def insights_search(q: str = Query(..., min_length=1), top_k: int = Query(3, ge=1, le=20)):
    try:
        return search_insights(q, top_k=top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index")
async def insights_index(payload: List[Dict[str, Any]], current_user: dict = Depends(get_current_user)):
    """Index documents into the vector store. Protected endpoint to avoid open injection.

    Payload shape: [{"text": "...", "meta": { ... }}, ...]
    """
    if not isinstance(payload, list) or not payload:
        raise HTTPException(status_code=400, detail="payload must be a non-empty list of documents")
    try:
        return index_documents(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
