"""Repository 패턴 구현"""
from .base import BaseRepository
from .news_repository import NewsRepository
from .article_repository import ArticleRepository

__all__ = [
    "BaseRepository",
    "NewsRepository",
    "ArticleRepository",
]

