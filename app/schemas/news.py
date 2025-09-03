"""
뉴스 관련 API 스키마
"""
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class NewsEntry(BaseModel):
    """extract_20250826_105701.json 구조의 뉴스 엔트리 모델"""
    guid: str = Field(..., description="뉴스 고유 식별자")
    source: str = Field(..., description="뉴스 소스")
    title: str = Field(..., description="뉴스 제목")
    link: str = Field(..., description="뉴스 링크")
    article_text: Optional[str] = Field(None, description="기사 전문")
    summary: Optional[str] = Field(None, description="뉴스 요약")
    tags: List[str] = Field(default_factory=list, description="태그 목록")
    content_type: str = Field("NEWS", description="콘텐츠 타입")
    language: str = Field("ENGLISH", description="언어")
    readability_score: Optional[float] = Field(None, description="가독성 점수")
    key_entities: List[str] = Field(default_factory=list, description="주요 엔티티")
    processed_at: Optional[str] = Field(None, description="처리 시간")
    text_length: Optional[int] = Field(None, description="텍스트 길이")


class NewsOut(BaseModel):
    """뉴스 아이템 출력 모델 (기존 호환성 유지)"""
    source: Optional[str] = Field(None, description="뉴스 소스")
    title: Optional[str] = Field(None, description="뉴스 제목")
    link: HttpUrl = Field(..., description="뉴스 링크")
    published: Optional[str] = Field(None, description="발행일시 (ISO 형식)")
    summary: Optional[str] = Field(None, description="뉴스 요약")
    authors: Optional[List[str]] = Field(None, description="작성자 목록")
    tags: Optional[List[str]] = Field(None, description="태그 목록")


class NewsDescriptionResponse(BaseModel):
    """뉴스 description 응답 모델"""
    success: bool = Field(..., description="요청 성공 여부")
    count: int = Field(..., description="조회된 뉴스 개수")
    data: List[NewsEntry] = Field(..., description="뉴스 엔트리 목록")
    total: int = Field(..., description="전체 뉴스 개수")


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
    group: Optional[str] = Field(None, description="특정 그룹 필터")
    limit: int = Field(20, ge=1, le=100, description="조회 개수")
    offset: int = Field(0, ge=0, description="오프셋")
    sort: str = Field("fresh", pattern="^(fresh|time)$", description="정렬 방식")
    refresh: bool = Field(False, description="캐시 새로고침")
