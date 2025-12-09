"""뉴스 API 라우터"""
from typing import List
from fastapi import APIRouter, Query, HTTPException, Depends

from ....schemas.news import (
    NewsOut, 
    HealthResponse, 
    NewsQuery, 
    NewsEntry, 
    NewsDescriptionResponse
)
from ....api.deps import get_news_service
from ....services.news_service import NewsService

router = APIRouter()


@router.get("/", response_model=List[NewsOut])
async def get_news(
    q: str = Query(None, description="검색어"),
    source: str = Query(None, description="특정 소스 필터"),
    group: str = Query(None, description="특정 그룹 필터"),
    limit: int = Query(20, ge=1, le=100, description="조회 개수"),
    offset: int = Query(0, ge=0, description="오프셋"),
    sort: str = Query("fresh", pattern="^(fresh|time)$", description="정렬 방식"),
    refresh: bool = Query(False, description="캐시 새로고침"),
    news_service: NewsService = Depends(get_news_service)
):
    """뉴스 목록 조회"""
    try:
        query = NewsQuery(
            q=q, source=source, group=group,
            limit=limit, offset=offset, sort=sort, refresh=refresh
        )
        
        data, total = await news_service.search_news(query)
        
        # NewsOut 형식으로 변환
        news_items = []
        for item in data:
            news_out = NewsOut(
                source=item.get('source'),
                title=item.get('title'),
                link=item.get('link'),
                published=item.get('published') or item.get('processed_at'),
                summary=item.get('summary'),
                authors=item.get('authors', []),
                tags=item.get('tags', [])
            )
            news_items.append(news_out)
        
        return news_items
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 조회 오류: {str(e)}")


@router.get("/description", response_model=NewsDescriptionResponse)
async def get_news_description(
    q: str = Query(None, description="검색어"),
    source: str = Query(None, description="특정 소스 필터"),
    group: str = Query(None, description="특정 그룹 필터"),
    limit: int = Query(20, ge=1, le=100, description="조회 개수"),
    offset: int = Query(0, ge=0, description="오프셋"),
    sort: str = Query("fresh", pattern="^(fresh|time)$", description="정렬 방식"),
    refresh: bool = Query(False, description="캐시 새로고침"),
    news_service: NewsService = Depends(get_news_service)
):
    """뉴스 description 응답 형식으로 조회"""
    try:
        query = NewsQuery(
            q=q, source=source, group=group,
            limit=limit, offset=offset, sort=sort, refresh=refresh
        )
        
        data, total = await news_service.search_news(query)
        
        # NewsEntry 형식으로 변환
        news_entries = []
        for item in data:
            news_entry = NewsEntry(
                guid=item.get('guid', str(item.get('id', ''))),
                source=item.get('source', ''),
                title=item.get('title', ''),
                link=item.get('link', ''),
                article_text=item.get('article_text'),
                summary=item.get('summary'),
                tags=item.get('tags', []),
                content_type=item.get('content_type', 'NEWS'),
                language=item.get('language', 'ENGLISH'),
                readability_score=item.get('readability_score'),
                key_entities=item.get('key_entities', []),
                processed_at=item.get('processed_at'),
                text_length=item.get('text_length')
            )
            news_entries.append(news_entry)
        
        return NewsDescriptionResponse(
            success=True,
            count=len(news_entries),
            data=news_entries,
            total=total
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 description 조회 오류: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health_check(
    news_service: NewsService = Depends(get_news_service)
):
    """헬스체크"""
    try:
        status = await news_service.get_health_status()
        return HealthResponse(
            ok=status["ok"],
            count=status["count"],
            backend=status["backend"],
            version=status["version"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"헬스체크 오류: {str(e)}")


@router.get("/sources")
async def get_sources(
    news_service: NewsService = Depends(get_news_service)
):
    """사용 가능한 뉴스 소스 목록"""
    try:
        sources = await news_service.get_sources()
        return {"sources": sources, "count": len(sources)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"소스 목록 조회 오류: {str(e)}")


@router.get("/groups")
async def get_groups(
    news_service: NewsService = Depends(get_news_service)
):
    """사용 가능한 뉴스 그룹 목록"""
    try:
        groups = await news_service.get_groups()
        return {"groups": groups, "count": len(groups)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"그룹 목록 조회 오류: {str(e)}")

