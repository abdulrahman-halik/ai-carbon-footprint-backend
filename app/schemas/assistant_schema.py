from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 300


class ChatResponse(BaseModel):
    reply: str
    model: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
