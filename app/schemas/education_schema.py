from pydantic import BaseModel, ConfigDict
from typing import Optional

class ArticleOut(BaseModel):
    id: str
    title: str
    excerpt: str
    category: str
    date: str
    readTime: str
    slug: str
    imageColor: Optional[str] = None
    body: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
