"""의존성 컨테이너 (Dependency Container)

Clean Architecture 원칙에 따라 객체 생성 로직을 중앙화합니다.
API와 CLI 모두 이 컨테이너를 통해 서비스를 생성합니다.
"""
from typing import Optional

from ..repositories import NewsRepository, ArticleRepository
from ..services.news_service import NewsService
from ..services.article_service import ArticleService


class Container:
    """의존성 컨테이너 - 서비스 인스턴스 생성 및 관리"""
    
    @staticmethod
    def get_news_repository() -> NewsRepository:
        """NewsRepository 인스턴스 반환"""
        return NewsRepository()
    
    @staticmethod
    def get_article_repository() -> ArticleRepository:
        """ArticleRepository 인스턴스 반환"""
        return ArticleRepository()
    
    @staticmethod
    def get_news_service(
        news_repo: Optional[NewsRepository] = None,
    ) -> NewsService:
        """NewsService 인스턴스 반환"""
        if news_repo is None:
            news_repo = Container.get_news_repository()
        return NewsService(news_repo=news_repo)
    
    @staticmethod
    def get_article_service(
        article_repo: Optional[ArticleRepository] = None,
    ) -> ArticleService:
        """ArticleService 인스턴스 반환"""
        if article_repo is None:
            article_repo = Container.get_article_repository()
        return ArticleService(article_repo=article_repo)

