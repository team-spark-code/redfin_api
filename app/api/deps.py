"""FastAPI 의존성 주입

FastAPI의 Depends를 위한 래퍼 함수들.
실제 객체 생성은 app.core.container.Container에서 담당합니다.
"""
from ..core.container import Container
from ..repositories import NewsRepository, ArticleRepository
from ..services.news_service import NewsService
from ..services.article_service import ArticleService


def get_news_repository() -> NewsRepository:
    """NewsRepository 인스턴스 반환 (FastAPI Depends용)"""
    return Container.get_news_repository()


def get_article_repository() -> ArticleRepository:
    """ArticleRepository 인스턴스 반환 (FastAPI Depends용)"""
    return Container.get_article_repository()


def get_news_service(
    news_repo: NewsRepository | None = None,
) -> NewsService:
    """NewsService 인스턴스 반환 (FastAPI Depends용)"""
    return Container.get_news_service(news_repo=news_repo)


def get_article_service(
    article_repo: ArticleRepository | None = None,
) -> ArticleService:
    """ArticleService 인스턴스 반환 (FastAPI Depends용)"""
    return Container.get_article_service(article_repo=article_repo)

