"""
Article 서비스 - CRUD 작업 처리
"""
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..repositories.article_repository import ArticleRepository
from ..models.article import Article, ArticleCreate, ArticleUpdate
from ..schemas.article import ArticleResponse, ArticleListResponse, CategoryInfo, CategoryListResponse, ARTICLE_CATEGORIES


class ArticleService:
    """Article CRUD 서비스"""
    
    def __init__(self, article_repo: Optional[ArticleRepository] = None):
        self.article_repo = article_repo or ArticleRepository()
    
    def _convert_to_response(self, doc: Dict[str, Any]) -> ArticleResponse:
        """MongoDB 문서를 응답 스키마로 변환"""
        try:
            # 필드명 매핑 (MongoDB 필드명 -> ArticleResponse 필드명)
            response_data = {
                "id": str(doc.get("_id", "unknown")),
                "title": doc.get("Title", "제목 없음"),
                "summary": doc.get("Summary"),
                "url": doc.get("URL"),
                "category": doc.get("category"),
                "body": doc.get("body"),
                "published_at": doc.get("published_at"),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at"),
                "hero_image_url": doc.get("hero_image_url"),
                "author_name": doc.get("author_name"),
            }
            
            # keywords 필드 처리
            if "keywords" in doc:
                if isinstance(doc["keywords"], str):
                    try:
                        import ast
                        response_data["keywords"] = ast.literal_eval(doc["keywords"])
                    except:
                        response_data["keywords"] = []
                elif isinstance(doc["keywords"], list):
                    response_data["keywords"] = doc["keywords"]
                else:
                    response_data["keywords"] = []
            else:
                response_data["keywords"] = []
            
            # tags 필드 처리
            if "tags" in doc and isinstance(doc["tags"], list):
                response_data["tags"] = doc["tags"]
            else:
                response_data["tags"] = []
            
            # sources 필드 처리
            if "sources" in doc and isinstance(doc["sources"], list):
                response_data["sources"] = doc["sources"]
            else:
                response_data["sources"] = []
            
            return ArticleResponse.model_validate(response_data)
        except Exception as e:
            print(f"문서 변환 오류: {e}, 문서: {doc}")
            # 기본값으로 ArticleResponse 생성
            return ArticleResponse(
                id=str(doc.get("_id", "unknown")),
                title=doc.get("Title", "제목 없음"),
                summary=doc.get("Summary"),
                url=doc.get("URL"),
                category=doc.get("category"),
                body=doc.get("body"),
                published_at=doc.get("published_at"),
                created_at=doc.get("created_at"),
                updated_at=doc.get("updated_at"),
                tags=doc.get("tags", []),
                keywords=doc.get("keywords", []),
                hero_image_url=doc.get("hero_image_url"),
                author_name=doc.get("author_name"),
                sources=doc.get("sources", [])
            )
    
    async def create_article(self, article_data: ArticleCreate) -> ArticleResponse:
        """새 기사 생성"""
        # 현재 시간으로 타임스탬프 설정
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        article_dict = article_data.model_dump(by_alias=True, exclude_unset=True)
        article_dict.update({
            "created_at": now,
            "updated_at": now
        })
        
        doc = await self.article_repo.create(article_dict)
        return self._convert_to_response(doc)
    
    async def get_article(self, article_id: str) -> Optional[ArticleResponse]:
        """ID로 기사 조회"""
        doc = await self.article_repo.find_by_id(article_id)
        if doc:
            return self._convert_to_response(doc)
        return None
    
    async def get_articles(
        self, 
        skip: int = 0, 
        limit: int = 10,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> ArticleListResponse:
        """기사 목록 조회"""
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
        
        # 전체 개수 조회
        total = await self.article_repo.count(filter_dict)
        
        # 목록 조회 (최신순 정렬)
        docs = await self.article_repo.find_many(
            filter_dict=filter_dict,
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )
        
        items = [self._convert_to_response(doc) for doc in docs]
        
        return ArticleListResponse(
            items=items,
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            size=limit
        )

    async def get_all_articles(self) -> ArticleListResponse:
        """모든 기사 조회"""
        docs = await self.article_repo.find_many(
            filter_dict={},
            skip=0,
            limit=10000,  # 충분히 큰 값
            sort=[("created_at", -1)]
        )
        
        items = [self._convert_to_response(doc) for doc in docs]
        
        return ArticleListResponse(
            items=items,
            total=len(items),
            page=1,
            size=len(items)
        )
    
    async def update_article(self, article_id: str, update_data: ArticleUpdate) -> Optional[ArticleResponse]:
        """기사 업데이트"""
        # None이 아닌 필드만 업데이트
        update_dict = {k: v for k, v in update_data.model_dump(by_alias=True, exclude_unset=True).items() if v is not None}
        
        if not update_dict:
            raise ValueError("업데이트할 데이터가 없습니다")
        
        # updated_at 필드 추가
        update_dict["updated_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        doc = await self.article_repo.update(article_id, update_dict)
        if doc:
            return self._convert_to_response(doc)
        return None
    
    async def delete_article(self, article_id: str) -> bool:
        """기사 삭제"""
        return await self.article_repo.delete(article_id)
    
    async def get_article_count(self) -> int:
        """전체 기사 개수 조회"""
        return await self.article_repo.count({})
    
    async def get_all_articles_from_both_collections(
        self, 
        skip: int = 0, 
        limit: int = 10,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> ArticleListResponse:
        """두 컬렉션(articles, news)에서 모든 기사 조회"""
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
        
        # 두 컬렉션에서 조회
        docs = await self.article_repo.find_from_both_collections(
            filter_dict=filter_dict,
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )
        
        # 전체 개수는 대략적으로 계산 (정확한 개수는 비용이 많이 듦)
        # 실제로는 두 컬렉션의 개수를 합산해야 하지만, 성능을 위해 근사치 사용
        total = len(docs) + skip  # 근사치
        
        items = [self._convert_to_response(doc) for doc in docs]
        
        return ArticleListResponse(
            items=items,
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            size=limit
        )
    
    async def get_categories(self) -> CategoryListResponse:
        """모든 카테고리 목록 조회 (각 카테고리별 기사 수 포함)"""
        categories = []
        
        for category_name, category_info in ARTICLE_CATEGORIES.items():
            # 두 컬렉션에서 해당 카테고리 기사 수 조회
            total_count = await self.article_repo.count_by_category(category_name)
            
            categories.append(CategoryInfo(
                name=category_info["name"],
                name_ko=category_info["name_ko"],
                description=category_info["description"],
                condition=category_info["condition"],
                count=total_count
            ))
        
        return CategoryListResponse(
            categories=categories,
            total=len(categories)
        )
    
    async def get_articles_by_category(
        self, 
        category: str,
        skip: int = 0, 
        limit: int = 10,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> ArticleListResponse:
        """특정 카테고리의 기사 조회"""
        # 유효한 카테고리인지 확인
        if category not in ARTICLE_CATEGORIES:
            raise ValueError(f"유효하지 않은 카테고리입니다: {category}")
        
        # 검색 조건 구성
        filter_dict = {"category": category}
        
        if search:
            filter_dict["$or"] = [
                {"Title": {"$regex": search, "$options": "i"}},
                {"Summary": {"$regex": search, "$options": "i"}},
                {"body": {"$regex": search, "$options": "i"}},
                {"keywords": {"$regex": search, "$options": "i"}}
            ]
        
        if tags:
            filter_dict["tags"] = {"$in": tags}
        
        # 두 컬렉션에서 조회
        docs = await self.article_repo.find_from_both_collections(
            filter_dict=filter_dict,
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )
        
        # 전체 개수는 근사치로 계산
        total = len(docs) + skip  # 근사치
        
        items = [self._convert_to_response(doc) for doc in docs]
        
        return ArticleListResponse(
            items=items,
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            size=limit
        )
