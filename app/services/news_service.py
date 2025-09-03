"""
뉴스 서비스 - 비즈니스 로직 처리
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.collection import Collection

from ..core.config import settings
from ..schemas.news import NewsEntry, NewsOut, NewsQuery

logger = logging.getLogger(__name__)


class NewsService:
    """뉴스 데이터 처리 서비스"""
    
    def __init__(self):
        self.backend = settings.backend
        self.news_file = settings.news_file
        self._cache: List[Dict[str, Any]] = []
        self._cache_timestamp: Optional[float] = None
        
        # MongoDB 연결 (백엔드가 MONGO인 경우)
        self.mongo_client: Optional[MongoClient] = None
        self.mongo_collection: Optional[Collection] = None
        
        if self.backend == "MONGO" and settings.mongo_uri:
            try:
                self.mongo_client = MongoClient(settings.mongo_uri)
                self.mongo_collection = self.mongo_client[settings.mongo_db][settings.mongo_col]
                logger.info(f"MongoDB 연결 성공: {settings.mongo_db}.{settings.mongo_col}")
            except Exception as e:
                logger.error(f"MongoDB 연결 실패: {e}")
                self.backend = "FILE"  # MongoDB 실패 시 파일 백엔드로 폴백
    
    def _load_file_data(self) -> List[Dict[str, Any]]:
        """파일에서 뉴스 데이터 로드"""
        try:
            if not self.news_file.exists():
                logger.warning(f"뉴스 파일이 존재하지 않음: {self.news_file}")
                return []
            
            data = []
            with open(self.news_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        if line.strip():
                            item = json.loads(line.strip())
                            data.append(item)
                    except json.JSONDecodeError as e:
                        logger.warning(f"라인 {line_num} JSON 파싱 오류: {e}")
                        continue
            
            logger.info(f"파일에서 {len(data)}개 뉴스 항목 로드")
            return data
            
        except Exception as e:
            logger.error(f"파일 데이터 로드 오류: {e}")
            return []
    
    def _load_mongo_data(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """MongoDB에서 뉴스 데이터 로드"""
        try:
            if not self.mongo_collection:
                logger.error("MongoDB 컬렉션이 초기화되지 않음")
                return []
            
            filter_query = query or {}
            cursor = self.mongo_collection.find(filter_query)
            data = list(cursor)
            
            logger.info(f"MongoDB에서 {len(data)}개 뉴스 항목 로드")
            return data
            
        except Exception as e:
            logger.error(f"MongoDB 데이터 로드 오류: {e}")
            return []
    
    def get_news_data(self, refresh: bool = False) -> List[Dict[str, Any]]:
        """뉴스 데이터 조회 (캐시 또는 백엔드에서)"""
        current_time = datetime.now().timestamp()
        
        # 캐시가 유효하고 새로고침이 아닌 경우 캐시 반환
        if (not refresh and self._cache and self._cache_timestamp and 
            current_time - self._cache_timestamp < 300):  # 5분 캐시
            return self._cache
        
        # 백엔드에서 데이터 로드
        if self.backend == "MONGO":
            data = self._load_mongo_data()
        else:
            data = self._load_file_data()
        
        # 캐시 업데이트
        self._cache = data
        self._cache_timestamp = current_time
        
        return data
    
    def search_news(self, query: NewsQuery) -> List[Dict[str, Any]]:
        """뉴스 검색"""
        data = self.get_news_data(refresh=query.refresh)
        
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
    
    def get_health_status(self) -> Dict[str, Any]:
        """헬스체크 상태 반환"""
        data = self.get_news_data()
        return {
            "ok": True,
            "count": len(data),
            "backend": self.backend,
            "version": "0.1.0"
        }
    
    def __del__(self):
        """소멸자 - MongoDB 연결 정리"""
        if self.mongo_client:
            self.mongo_client.close()


# 전역 서비스 인스턴스
news_service = NewsService()
