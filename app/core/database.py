"""
MongoDB 데이터베이스 연결 관리
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from typing import Optional

from .config import settings


class Database:
    """MongoDB 데이터베이스 연결 클래스"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self) -> None:
        """MongoDB에 연결"""
        try:
            self.client = AsyncIOMotorClient(settings.mongo_uri)
            self.database = self.client[settings.mongo_db]
            
            # 연결 테스트
            await self.client.admin.command('ping')
            print(f"MongoDB 연결 성공: {settings.mongo_db}")
            
        except ConnectionFailure as e:
            print(f"MongoDB 연결 실패: {e}")
            raise
    
    async def disconnect(self) -> None:
        """MongoDB 연결 해제"""
        if self.client:
            self.client.close()
            print("MongoDB 연결 해제")
    
    def get_collection(self, collection_name: str):
        """컬렉션 가져오기"""
        if self.database is None:
            raise RuntimeError("데이터베이스가 연결되지 않았습니다")
        return self.database[collection_name]


# 전역 데이터베이스 인스턴스
database = Database()
