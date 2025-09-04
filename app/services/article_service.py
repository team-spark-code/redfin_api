"""
Article 서비스 - CRUD 작업 처리
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from ..core.database import database
from ..core.config import settings
from ..models.article import Article, ArticleCreate, ArticleUpdate
from ..schemas.article import ArticleResponse, ArticleListResponse


class ArticleService:
    """Article CRUD 서비스"""
    
    def __init__(self):
        self.articles_collection_name = settings.mongo_articles_col
        self.news_collection_name = settings.mongo_news_col
    
    def _get_articles_collection(self):
        """Articles 컬렉션 가져오기"""
        return database.get_collection(self.articles_collection_name)
    
    def _get_news_collection(self):
        """News 컬렉션 가져오기"""
        return database.get_collection(self.news_collection_name)
    
    def _convert_to_response(self, doc: Dict[str, Any]) -> ArticleResponse:
        """MongoDB 문서를 응답 스키마로 변환"""
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        return ArticleResponse(**doc)
    
    async def create_article(self, article_data: ArticleCreate) -> ArticleResponse:
        """새 기사 생성"""
        collection = self._get_articles_collection()
        
        # 현재 시간으로 타임스탬프 설정
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        article_dict = article_data.model_dump(by_alias=True, exclude_unset=True)
        article_dict.update({
            "created_at": now,
            "updated_at": now
        })
        
        try:
            result = await collection.insert_one(article_dict)
            article_dict["_id"] = result.inserted_id
            return self._convert_to_response(article_dict)
        except DuplicateKeyError:
            raise ValueError("중복된 기사가 이미 존재합니다")
    
    async def get_article(self, article_id: str) -> Optional[ArticleResponse]:
        """ID로 기사 조회"""
        collection = self._get_articles_collection()
        
        try:
            doc = await collection.find_one({"_id": ObjectId(article_id)})
            if doc:
                return self._convert_to_response(doc)
            return None
        except Exception:
            return None
    
    async def get_articles(
        self, 
        skip: int = 0, 
        limit: int = 10,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> ArticleListResponse:
        """기사 목록 조회"""
        collection = self._get_articles_collection()
        
        # 검색 조건 구성
        filter_dict = {}
        
        if search:
            filter_dict["$or"] = [
                {"Title": {"$regex": search, "$options": "i"}},
                {"Summary": {"$regex": search, "$options": "i"}},
                {"body": {"$regex": search, "$options": "i"}},
                {"keywords": {"$regex": search, "$options": "i"}}
            ]
        
        if tags:
            filter_dict["tags"] = {"$in": tags}
        
        # 목록 조회 (정렬 없이)
        cursor = collection.find(filter_dict).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        
        # 전체 개수 조회 (간단한 방식)
        try:
            total = await collection.count_documents(filter_dict)
        except Exception:
            # count_documents가 실패하면 find로 대략적인 개수 계산
            total = len(docs) if docs else 0
        
        items = [self._convert_to_response(doc) for doc in docs]
        
        return ArticleListResponse(
            items=items,
            total=total,
            page=(skip // limit) + 1,
            size=limit
        )
    
    async def update_article(self, article_id: str, update_data: ArticleUpdate) -> Optional[ArticleResponse]:
        """기사 업데이트"""
        collection = self._get_articles_collection()
        
        # None이 아닌 필드만 업데이트
        update_dict = {k: v for k, v in update_data.model_dump(by_alias=True, exclude_unset=True).items() if v is not None}
        
        if not update_dict:
            raise ValueError("업데이트할 데이터가 없습니다")
        
        # updated_at 필드 추가
        update_dict["updated_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            result = await collection.update_one(
                {"_id": ObjectId(article_id)},
                {"$set": update_dict}
            )
            
            if result.matched_count == 0:
                return None
            
            # 업데이트된 문서 반환
            return await self.get_article(article_id)
        except Exception:
            return None
    
    async def delete_article(self, article_id: str) -> bool:
        """기사 삭제"""
        collection = self._get_articles_collection()
        
        try:
            result = await collection.delete_one({"_id": ObjectId(article_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    async def get_article_count(self) -> int:
        """전체 기사 개수 조회"""
        try:
            collection = self._get_articles_collection()
            # count_documents 대신 find를 사용하여 개수 계산
            cursor = collection.find({})
            docs = await cursor.to_list(length=None)
            return len(docs)
        except Exception:
            return 0
    
    async def get_all_articles_from_both_collections(
        self, 
        skip: int = 0, 
        limit: int = 10,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> ArticleListResponse:
        """두 컬렉션(articles, news)에서 모든 기사 조회"""
        try:
            # Articles 컬렉션에서 조회
            articles_collection = self._get_articles_collection()
            news_collection = self._get_news_collection()
            
            # 검색 조건 구성
            filter_dict = {}
            
            if search:
                filter_dict["$or"] = [
                    {"Title": {"$regex": search, "$options": "i"}},
                    {"Summary": {"$regex": search, "$options": "i"}},
                    {"body": {"$regex": search, "$options": "i"}},
                    {"keywords": {"$regex": search, "$options": "i"}}
                ]
            
            if tags:
                filter_dict["tags"] = {"$in": tags}
            
            # Articles 컬렉션에서 조회
            articles_cursor = articles_collection.find(filter_dict)
            articles_docs = await articles_cursor.to_list(length=None)
            
            # News 컬렉션에서 조회
            news_cursor = news_collection.find(filter_dict)
            news_docs = await news_cursor.to_list(length=None)
            
            # 두 컬렉션의 결과를 합치기
            all_docs = articles_docs + news_docs
            
            # 전체 개수
            total = len(all_docs)
            
            # 페이지네이션 적용
            paginated_docs = all_docs[skip:skip + limit]
            
            # 응답 형식으로 변환
            items = [self._convert_to_response(doc) for doc in paginated_docs]
            
            return ArticleListResponse(
                items=items,
                total=total,
                page=(skip // limit) + 1,
                size=limit
            )
        except Exception as e:
            print(f"두 컬렉션 조회 중 오류: {e}")
            # 오류 발생 시 빈 결과 반환
            return ArticleListResponse(
                items=[],
                total=0,
                page=1,
                size=limit
            )


# 전역 서비스 인스턴스
article_service = ArticleService()
