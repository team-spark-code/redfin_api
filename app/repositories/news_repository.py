"""News Repository - 뉴스 데이터 접근 계층"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.collection import Collection

from .base import BaseRepository
from ..core.config import settings

logger = logging.getLogger(__name__)


class NewsRepository(BaseRepository):
    """뉴스 데이터 Repository"""
    
    def __init__(self):
        super().__init__(settings.mongo_news_col)
        self.backend = settings.backend
        self.news_file = settings.news_file
        
        # MongoDB 연결 (백엔드가 MONGO인 경우)
        self.mongo_client: Optional[MongoClient] = None
        self.mongo_collection: Optional[Collection] = None
        
        if self.backend == "MONGO" and settings.mongo_uri:
            try:
                self.mongo_client = MongoClient(settings.mongo_uri)
                self.mongo_collection = self.mongo_client[settings.mongo_db][settings.mongo_news_col]
                logger.info(f"MongoDB 연결 성공: {settings.mongo_db}.{settings.mongo_news_col}")
            except Exception as e:
                logger.error(f"MongoDB 연결 실패: {e}")
                self.backend = "FILE"  # MongoDB 실패 시 파일 백엔드로 폴백
    
    def _load_file_data(self) -> List[Dict[str, Any]]:
        """파일에서 뉴스 데이터 로드 (동기)"""
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
    
    def _load_mongo_data_sync(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """MongoDB에서 뉴스 데이터 로드 (동기)"""
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
    
    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """ID로 뉴스 조회"""
        if self.backend == "MONGO":
            if self.mongo_collection:
                return self.mongo_collection.find_one({"_id": id})
        # 파일 백엔드는 ID 조회 미지원
        return None
    
    async def find_many(
        self, 
        filter_dict: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """여러 뉴스 조회"""
        if self.backend == "MONGO":
            if self.mongo_collection:
                cursor = self.mongo_collection.find(filter_dict or {})
                if sort:
                    cursor = cursor.sort(sort)
                cursor = cursor.skip(skip).limit(limit)
                return list(cursor)
        
        # 파일 백엔드
        data = self._load_file_data()
        
        # 필터링 (간단한 구현)
        if filter_dict:
            filtered_data = []
            for item in data:
                match = True
                for key, value in filter_dict.items():
                    if item.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_data.append(item)
            data = filtered_data
        
        # 정렬
        if sort:
            for field, direction in reversed(sort):
                data.sort(key=lambda x: x.get(field, ''), reverse=(direction == -1))
        
        # 페이징
        return data[skip:skip + limit]
    
    async def get_all(self) -> List[Dict[str, Any]]:
        """모든 뉴스 조회"""
        if self.backend == "MONGO":
            return self._load_mongo_data_sync()
        return self._load_file_data()
    
    async def get_sources(self) -> List[str]:
        """사용 가능한 소스 목록 조회"""
        data = await self.get_all()
        sources = list(set(item.get('source', '') for item in data if item.get('source')))
        sources.sort()
        return sources
    
    async def get_groups(self) -> List[str]:
        """사용 가능한 그룹 목록 조회"""
        data = await self.get_all()
        groups = list(set(item.get('group', '') for item in data if item.get('group')))
        groups.sort()
        return groups
    
    def __del__(self):
        """소멸자 - MongoDB 연결 정리"""
        if self.mongo_client:
            self.mongo_client.close()

