"""
News API routes — thin controllers delegating to backend.services.news
"""

from fastapi import APIRouter, Query, HTTPException, Depends

from backend.core.deps import get_current_user_id
from backend.services.news import get_news, fetch_full_article, _is_safe_url

router = APIRouter()


@router.get("/crypto")
async def get_crypto_news(_user_id: int = Depends(get_current_user_id)):
    """Get latest crypto news from RSS feeds."""
    items = await get_news("crypto")
    return {"items": items, "category": "crypto"}


@router.get("/forex")
async def get_forex_news(_user_id: int = Depends(get_current_user_id)):
    """Get latest forex news from RSS feeds."""
    items = await get_news("forex")
    return {"items": items, "category": "forex"}


@router.get("/article")
async def get_article(
    url: str = Query(..., description="Article URL to fetch"),
    _user_id: int = Depends(get_current_user_id),
):
    """Fetch and parse a full article from its URL."""
    if not url or not _is_safe_url(url):
        raise HTTPException(status_code=400, detail="Invalid or unsafe URL")
    return await fetch_full_article(url)
