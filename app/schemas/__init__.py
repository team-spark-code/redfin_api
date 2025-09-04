"""
API 요청/응답 스키마 정의
"""

from .news import (
    NewsEntry,
    NewsOut,
    NewsDescriptionResponse,
    HealthResponse,
    NewsQuery
)

from .article import (
    ArticleResponse,
    ArticleCreateRequest,
    ArticleUpdateRequest,
    ArticleListResponse
)

__all__ = [
    "NewsEntry",
    "NewsOut", 
    "NewsDescriptionResponse",
    "HealthResponse",
    "NewsQuery",
    "ArticleResponse",
    "ArticleCreateRequest", 
    "ArticleUpdateRequest",
    "ArticleListResponse"
]
