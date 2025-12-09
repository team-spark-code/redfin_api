"""Article Repository - 기사 데이터 접근 계층"""
from typing import List, Dict, Any, Optional
from bson import ObjectId

from .base import BaseRepository
from ..core.config import settings


class ArticleRepository(BaseRepository):
    """기사 데이터 Repository"""
    
    def __init__(self):
        super().__init__(settings.mongo_articles_col)
        self.news_collection_name = settings.mongo_news_col
    
    @property
    def news_collection(self):
        """News 컬렉션 인스턴스 반환"""
        return self.db[self.news_collection_name]
    
    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """ID로 기사 조회"""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(id)})
            return doc
        except Exception:
            return None
    
    async def find_many(
        self, 
        filter_dict: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """여러 기사 조회"""
        if filter_dict is None:
            filter_dict = {}
        
        if sort is None:
            sort = [("created_at", -1)]
        
        cursor = self.collection.find(filter_dict).sort(sort).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return docs
    
    async def find_from_both_collections(
        self,
        filter_dict: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """Articles와 News 두 컬렉션에서 기사 조회"""
        if filter_dict is None:
            filter_dict = {}
        
        if sort is None:
            sort = [("created_at", -1)]
        
        # Articles 컬렉션에서 조회
        articles_cursor = self.collection.find(filter_dict).sort(sort)
        articles_docs = await articles_cursor.to_list(length=None)
        
        # News 컬렉션에서 조회
        news_cursor = self.news_collection.find(filter_dict).sort(sort)
        news_docs = await news_cursor.to_list(length=None)
        
        # 두 컬렉션의 결과를 합치기
        all_docs = articles_docs + news_docs
        
        # 정렬 (메모리에서)
        for field, direction in reversed(sort):
            all_docs.sort(
                key=lambda x: x.get(field, '') if x.get(field) else '',
                reverse=(direction == -1)
            )
        
        # 페이징
        return all_docs[skip:skip + limit]
    
    async def create(self, article_dict: Dict[str, Any]) -> Dict[str, Any]:
        """기사 생성"""
        result = await self.collection.insert_one(article_dict)
        article_dict["_id"] = result.inserted_id
        return article_dict
    
    async def update(self, article_id: str, update_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """기사 업데이트"""
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(article_id)},
                {"$set": update_dict}
            )
            
            if result.matched_count == 0:
                return None
            
            return await self.find_by_id(article_id)
        except Exception:
            return None
    
    async def delete(self, article_id: str) -> bool:
        """기사 삭제"""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(article_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    async def count_by_category(self, category: str) -> int:
        """카테고리별 기사 개수 조회 (두 컬렉션 합계)"""
        articles_count = await self.collection.count_documents({"category": category})
        news_count = await self.news_collection.count_documents({"category": category})
        return articles_count + news_count

