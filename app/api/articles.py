"""
Article API 라우터 - CRUD 엔드포인트
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse

from ..services.article_service import article_service
from ..schemas.article import (
    ArticleResponse,
    ArticleCreateRequest,
    ArticleUpdateRequest,
    ArticleListResponse
)
from ..models.article import ArticleCreate, ArticleUpdate

# 라우터 생성
router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("/", response_model=ArticleResponse, status_code=201)
async def create_article(article_data: ArticleCreateRequest):
    """새 기사 생성"""
    try:
        # 요청 스키마를 모델로 변환 (alias 사용)
        article_create = ArticleCreate(**article_data.model_dump(by_alias=True))
        
        # 서비스 호출
        result = await article_service.create_article(article_create)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기사 생성 중 오류가 발생했습니다: {str(e)}")


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: str = Path(..., description="기사 ID", example="68b97ad1e7c23a73720de215")
):
    """ID로 기사 조회"""
    result = await article_service.get_article(article_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="기사를 찾을 수 없습니다")
    
    return result


@router.get("/", response_model=ArticleListResponse)
async def get_articles(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=200, description="페이지 크기"),
    search: Optional[str] = Query(None, description="검색어 (제목, 요약, 본문, 키워드)"),
    tags: Optional[List[str]] = Query(None, description="태그 필터"),
    include_news: bool = Query(False, description="news 컬렉션도 포함하여 조회")
):
    """기사 목록 조회"""
    try:
        skip = (page - 1) * size
        
        if include_news:
            # 두 컬렉션 모두에서 조회
            result = await article_service.get_all_articles_from_both_collections(
                skip=skip,
                limit=size,
                search=search,
                tags=tags
            )
        else:
            # articles 컬렉션만 조회
            result = await article_service.get_articles(
                skip=skip,
                limit=size,
                search=search,
                tags=tags
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기사 목록 조회 중 오류가 발생했습니다: {str(e)}")


@router.get("/all", response_model=ArticleListResponse)
async def get_all_articles():
    """articles 컬렉션의 전체 기사 조회 (페이지네이션 없음)"""
    try:
        # articles 컬렉션 전체 조회
        result = await article_service.get_articles(
            skip=0,
            limit=1000,  # 합리적인 크기로 설정
            search=None,
            tags=None
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"전체 기사 조회 중 오류가 발생했습니다: {str(e)}")


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: str = Path(..., description="기사 ID", example="68b97ad1e7c23a73720de215"),
    update_data: ArticleUpdateRequest = None
):
    """기사 업데이트"""
    try:
        # 요청 스키마를 모델로 변환 (alias 사용)
        article_update = ArticleUpdate(**update_data.model_dump(by_alias=True, exclude_unset=True))
        
        # 서비스 호출
        result = await article_service.update_article(article_id, article_update)
        
        if not result:
            raise HTTPException(status_code=404, detail="기사를 찾을 수 없습니다")
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기사 업데이트 중 오류가 발생했습니다: {str(e)}")


@router.delete("/{article_id}")
async def delete_article(
    article_id: str = Path(..., description="기사 ID", example="68b97ad1e7c23a73720de215")
):
    """기사 삭제"""
    try:
        success = await article_service.delete_article(article_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="기사를 찾을 수 없습니다")
        
        return JSONResponse(
            status_code=200,
            content={"message": "기사가 성공적으로 삭제되었습니다", "id": article_id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기사 삭제 중 오류가 발생했습니다: {str(e)}")


@router.get("/stats/count")
async def get_article_count():
    """전체 기사 개수 조회"""
    try:
        count = await article_service.get_article_count()
        return {"total_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기사 개수 조회 중 오류가 발생했습니다: {str(e)}")


@router.get("/health/check")
async def health_check():
    """Article 서비스 헬스체크"""
    try:
        # 간단한 데이터베이스 연결 테스트
        count = await article_service.get_article_count()
        return {
            "status": "healthy",
            "service": "article",
            "database": "connected",
            "total_articles": count
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "article",
                "database": "disconnected",
                "error": str(e)
            }
        )
