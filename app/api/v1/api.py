"""API v1 라우터 통합"""
from fastapi import APIRouter

from .endpoints import news, articles

api_router = APIRouter()

api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(articles.router, prefix="/articles", tags=["articles"])

