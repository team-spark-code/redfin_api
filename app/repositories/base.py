"""Base Repository 추상 클래스"""
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.database import Database

from ..core.database import database


class BaseRepository(ABC):
    """Repository 패턴의 기본 추상 클래스"""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
    
    @property
    def db(self) -> AsyncIOMotorDatabase:
        """비동기 데이터베이스 인스턴스 반환"""
        if database.database is None:
            raise RuntimeError("데이터베이스가 연결되지 않았습니다")
        return database.database
    
    @property
    def collection(self):
        """컬렉션 인스턴스 반환"""
        return self.db[self.collection_name]
    
    @abstractmethod
    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """ID로 문서 조회"""
        pass
    
    @abstractmethod
    async def find_many(
        self, 
        filter_dict: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """여러 문서 조회"""
        pass
    
    async def count(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """문서 개수 조회"""
        if filter_dict is None:
            filter_dict = {}
        return await self.collection.count_documents(filter_dict)

