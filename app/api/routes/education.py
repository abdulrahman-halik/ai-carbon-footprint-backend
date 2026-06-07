from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.education_schema import ArticleOut
from app.services.education_service import get_all_articles, get_article_by_slug

router = APIRouter()

@router.get("/articles", response_model=List[ArticleOut])
async def list_articles():
    try:
        return get_all_articles()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/articles/{slug}", response_model=ArticleOut)
async def read_article(slug: str):
    try:
        return get_article_by_slug(slug)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
