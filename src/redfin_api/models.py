from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

class NewsOut(BaseModel):
    """뉴스 아이템 출력 모델"""
    source: Optional[str] = Field(None, description="뉴스 소스")
    title: Optional[str] = Field(None, description="뉴스 제목")
    link: HttpUrl = Field(..., description="뉴스 링크")
    published: Optional[str] = Field(None, description="발행일시 (ISO 형식)")
    summary: Optional[str] = Field(None, description="뉴스 요약")
    authors: Optional[List[str]] = Field(None, description="작성자 목록")
    tags: Optional[List[str]] = Field(None, description="태그 목록")

class HealthResponse(BaseModel):
    """헬스체크 응답 모델"""
    ok: bool = Field(..., description="서비스 상태")
    count: int = Field(..., description="캐시된 뉴스 개수")
    backend: str = Field(..., description="사용 중인 백엔드")
    version: str = Field(..., description="API 버전")

class NewsQuery(BaseModel):
    """뉴스 조회 쿼리 모델"""
    q: Optional[str] = Field(None, description="검색어")
    source: Optional[str] = Field(None, description="특정 소스 필터")
    limit: int = Field(20, ge=1, le=100, description="조회 개수")
    offset: int = Field(0, ge=0, description="오프셋")
    sort: str = Field("fresh", pattern="^(fresh|time)$", description="정렬 방식")
    refresh: bool = Field(False, description="캐시 새로고침")
