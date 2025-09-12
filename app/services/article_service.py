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
from ..schemas.article import ArticleResponse, ArticleListResponse, CategoryInfo, CategoryListResponse, ARTICLE_CATEGORIES


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
        """새 근냥 ㅋ 생성"""
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
        try:
            collection = self._get_articles_collection()
            print(f"컬렉션 가져오기 성공: {self.articles_collection_name}")
            
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
            
            print(f"필터 조건: {filter_dict}")
            
            # 전체 개수 조회 (count_documents 사용)
            try:
                total = await collection.count_documents(filter_dict)
                print(f"전체 문서 수: {total}")
            except Exception as e:
                print(f"count_documents 실패, find로 대체: {e}")
                # count_documents가 실패하면 find로 대체
                try:
                    all_docs = await collection.find(filter_dict).to_list(length=None)
                    total = len(all_docs)
                    print(f"find로 조회한 전체 문서 수: {total}")
                except Exception as e2:
                    print(f"find도 실패: {e2}")
                    total = 0
            
            # 목록 조회 (최신순 정렬)
            cursor = collection.find(filter_dict).sort("created_at", -1).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            print(f"조회된 문서 수: {len(docs)}")
            
            items = [self._convert_to_response(doc) for doc in docs]
            print(f"변환된 아이템 수: {len(items)}")
            
            return ArticleListResponse(
                items=items,
                total=total,
                page=(skip // limit) + 1 if limit > 0 else 1,
                size=limit
            )
        except Exception as e:
            print(f"get_articles 오류: {e}")
            raise

    async def get_all_articles(self) -> ArticleListResponse:
        """모든 기사 조회"""
        try:
            collection = self._get_articles_collection()
            print(f"컬렉션 가져오기 성공: {self.articles_collection_name}")
            
            cursor = collection.find({}).sort("created_at", -1)
            docs = await cursor.to_list(length=None)
            print(f"조회된 문서 수: {len(docs)}")
            
            items = [self._convert_to_response(doc) for doc in docs]
            print(f"변환된 아이템 수: {len(items)}")
            
            return ArticleListResponse(
                items=items,
                total=len(items),
                page=1,
                size=len(items)
            )
        except Exception as e:
            print(f"get_all_articles 오류: {e}")
            return ArticleListResponse(
                items=[],
                total=0,
                page=1,
                size=0
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
            
            print(f"두 컬렉션 조회 - 필터 조건: {filter_dict}")
            
            # Articles 컬렉션에서 조회 (최신순 정렬)
            articles_cursor = articles_collection.find(filter_dict).sort("created_at", -1)
            articles_docs = await articles_cursor.to_list(length=None)
            print(f"Articles 컬렉션에서 조회된 문서 수: {len(articles_docs)}")
            
            # News 컬렉션에서 조회 (최신순 정렬)
            news_cursor = news_collection.find(filter_dict).sort("created_at", -1)
            news_docs = await news_cursor.to_list(length=None)
            print(f"News 컬렉션에서 조회된 문서 수: {len(news_docs)}")
            
            # 두 컬렉션의 결과를 합치기
            all_docs = articles_docs + news_docs
            
            # 전체 개수
            total = len(all_docs)
            print(f"두 컬렉션 합계 문서 수: {total}")
            
            # 페이지네이션 적용
            paginated_docs = all_docs[skip:skip + limit]
            print(f"페이지네이션 적용 후 문서 수: {len(paginated_docs)}")
            
            # 응답 형식으로 변환
            items = [self._convert_to_response(doc) for doc in paginated_docs]
            print(f"변환된 아이템 수: {len(items)}")
            
            return ArticleListResponse(
                items=items,
                total=total,
                page=(skip // limit) + 1 if limit > 0 else 1,
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
    
    async def get_categories(self) -> CategoryListResponse:
        """모든 카테고리 목록 조회 (각 카테고리별 기사 수 포함)"""
        try:
            articles_collection = self._get_articles_collection()
            news_collection = self._get_news_collection()
            
            categories = []
            
            for category_name, category_info in ARTICLE_CATEGORIES.items():
                # Articles 컬렉션에서 해당 카테고리 기사 수 조회
                articles_count = await articles_collection.count_documents({"category": category_name})
                
                # News 컬렉션에서 해당 카테고리 기사 수 조회
                news_count = await news_collection.count_documents({"category": category_name})
                
                total_count = articles_count + news_count
                
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
        except Exception as e:
            print(f"카테고리 조회 오류: {e}")
            # 오류 발생 시 기본 카테고리 정보만 반환
            categories = []
            for category_name, category_info in ARTICLE_CATEGORIES.items():
                categories.append(CategoryInfo(
                    name=category_info["name"],
                    name_ko=category_info["name_ko"],
                    description=category_info["description"],
                    condition=category_info["condition"],
                    count=0
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
        try:
            # 유효한 카테고리인지 확인
            if category not in ARTICLE_CATEGORIES:
                raise ValueError(f"유효하지 않은 카테고리입니다: {category}")
            
            articles_collection = self._get_articles_collection()
            news_collection = self._get_news_collection()
            
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
            
            print(f"카테고리별 조회 - 카테고리: {category}, 필터 조건: {filter_dict}")
            
            # Articles 컬렉션에서 조회
            articles_cursor = articles_collection.find(filter_dict).sort("created_at", -1)
            articles_docs = await articles_cursor.to_list(length=None)
            print(f"Articles 컬렉션에서 조회된 문서 수: {len(articles_docs)}")
            
            # News 컬렉션에서 조회
            news_cursor = news_collection.find(filter_dict).sort("created_at", -1)
            news_docs = await news_cursor.to_list(length=None)
            print(f"News 컬렉션에서 조회된 문서 수: {len(news_docs)}")
            
            # 두 컬렉션의 결과를 합치기
            all_docs = articles_docs + news_docs
            
            # 전체 개수
            total = len(all_docs)
            print(f"카테고리 '{category}' 총 문서 수: {total}")
            
            # 페이지네이션 적용
            paginated_docs = all_docs[skip:skip + limit]
            print(f"페이지네이션 적용 후 문서 수: {len(paginated_docs)}")
            
            # 응답 형식으로 변환
            items = [self._convert_to_response(doc) for doc in paginated_docs]
            print(f"변환된 아이템 수: {len(items)}")
            
            return ArticleListResponse(
                items=items,
                total=total,
                page=(skip // limit) + 1 if limit > 0 else 1,
                size=limit
            )
        except Exception as e:
            print(f"카테고리별 기사 조회 중 오류: {e}")
            raise


# 전역 서비스 인스턴스
article_service = ArticleService()
