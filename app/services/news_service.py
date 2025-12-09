"""
뉴스 서비스 - 비즈니스 로직 처리
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..repositories.news_repository import NewsRepository
from ..schemas.news import NewsEntry, NewsOut, NewsQuery

logger = logging.getLogger(__name__)


class NewsService:
    """뉴스 데이터 처리 서비스"""
    
    def __init__(self, news_repo: Optional[NewsRepository] = None):
        self.news_repo = news_repo or NewsRepository()
        self._cache: List[Dict[str, Any]] = []
        self._cache_timestamp: Optional[float] = None
    
    async def get_news_data(self, refresh: bool = False) -> List[Dict[str, Any]]:
        """뉴스 데이터 조회 (캐시 또는 백엔드에서)"""
        current_time = datetime.now().timestamp()
        
        # 캐시가 유효하고 새로고침이 아닌 경우 캐시 반환
        if (not refresh and self._cache and self._cache_timestamp and 
            current_time - self._cache_timestamp < 300):  # 5분 캐시
            return self._cache
        
        # Repository를 통해 데이터 로드
        data = await self.news_repo.get_all()
        
        # 캐시 업데이트
        self._cache = data
        self._cache_timestamp = current_time
        
        return data
    
    async def search_news(self, query: NewsQuery) -> tuple[List[Dict[str, Any]], int]:
        """뉴스 검색"""
        data = await self.get_news_data(refresh=query.refresh)
        
        # 검색어 필터링
        if query.q:
            filtered_data = []
            search_term = query.q.lower()
            for item in data:
                title = item.get('title', '').lower()
                summary = item.get('summary', '').lower()
                content = item.get('article_text', '').lower()
                
                if (search_term in title or 
                    search_term in summary or 
                    search_term in content):
                    filtered_data.append(item)
            data = filtered_data
        
        # 소스 필터링
        if query.source:
            data = [item for item in data if item.get('source') == query.source]
        
        # 그룹 필터링
        if query.group:
            data = [item for item in data if item.get('group') == query.group]
        
        # 정렬
        if query.sort == "time":
            # 시간순 정렬 (published 또는 processed_at 기준)
            data.sort(key=lambda x: x.get('published') or x.get('processed_at') or '', reverse=True)
        else:
            # 신선도 점수 기반 정렬
            data.sort(key=lambda x: self._calculate_freshness_score(x), reverse=True)
        
        # 페이징
        total = len(data)
        start = query.offset
        end = start + query.limit
        data = data[start:end]
        
        return data, total
    
    def _calculate_freshness_score(self, item: Dict[str, Any]) -> float:
        """뉴스 아이템의 신선도 점수 계산"""
        now_ts = datetime.now().timestamp()
        
        # published 필드 우선 확인
        dt_str = item.get("published")
        if not dt_str:
            # processed_at 필드 확인
            dt_str = item.get("processed_at")
        
        if not dt_str:
            return 0.0
        
        try:
            # 다양한 날짜 형식 처리
            dt = None
            
            # 1. RFC 2822 형식 (예: "Mon, 25 Aug 2025 06:00:00 GMT")
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(dt_str)
            except:
                pass
            
            # 2. ISO 형식 (예: "2025-08-26T11:47:10.173932")
            if not dt:
                try:
                    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                except:
                    pass
            
            # 3. 다른 형식들 시도
            if not dt:
                try:
                    dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
                except:
                    pass
            
            if dt:
                age_h = max(1.0, (now_ts - dt.timestamp()) / 3600.0)
                return 1.0 / age_h
            else:
                logger.warning(f"지원되지 않는 날짜 형식: {dt_str}")
                return 0.0
                
        except Exception as e:
            logger.warning(f"날짜 파싱 오류: {e}")
            return 0.0
    
    async def get_health_status(self) -> Dict[str, Any]:
        """헬스체크 상태 반환"""
        data = await self.get_news_data()
        return {
            "ok": True,
            "count": len(data),
            "backend": self.news_repo.backend,
            "version": "0.2.0"
        }
    
    async def get_sources(self) -> List[str]:
        """사용 가능한 소스 목록 조회"""
        return await self.news_repo.get_sources()
    
    async def get_groups(self) -> List[str]:
        """사용 가능한 그룹 목록 조회"""
        return await self.news_repo.get_groups()
