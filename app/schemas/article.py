"""
Article 스키마 정의 (API 요청/응답)
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ArticleResponse(BaseModel):
    """Article 응답 스키마"""
    id: str = Field(..., description="기사 ID")
    title: str = Field(..., alias="Title", description="기사 제목")
    summary: Optional[str] = Field(None, alias="Summary", description="기사 요약")
    url: Optional[str] = Field(None, alias="URL", description="원본 URL")
    keywords: Optional[str] = Field(None, alias="keywords", description="키워드 (문자열)")
    category: Optional[str] = Field(None, alias="category", description="카테고리")
    body: Optional[str] = Field(None, alias="body", description="본문")
    published_at: Optional[str] = Field(None, alias="published_at", description="발행일시 (문자열)")
    tags: List[str] = Field(default_factory=list, alias="tags", description="태그 목록")
    updated_at: Optional[str] = Field(None, alias="updated_at", description="수정일시")
    created_at: Optional[str] = Field(None, alias="created_at", description="생성일시")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        },
        "json_schema_extra": {
            "example": {
                "id": "68b97ad1e7c23a73720de215",
                "Title": "Google discontinues Clips, the AI-powered camera you forgot about",
                "Summary": "While Google was busy showcasing its latest devices yesterday...",
                "URL": "https://assets.msn.com/labs/mind/AAIT1gq.html",
                "keywords": "['latest devices yesterday', 'Google discontinues Clips']",
                "category": "Incidents & Safety",
                "body": "While Google was busy showcasing its latest devices yesterday...",
                "published_at": "2019-10-16 00:00:00",
                "tags": ["policy/Regulation", "topic/Safety", "geo/US"],
                "updated_at": "2025-09-04 19:30:43",
                "created_at": "2025-09-04 19:30:43"
            }
        }
    }


class ArticleCreateRequest(BaseModel):
    """Article 생성 요청 스키마"""
    title: str = Field(..., alias="Title", min_length=1, max_length=500, description="기사 제목")
    summary: Optional[str] = Field(None, alias="Summary", description="기사 요약")
    url: Optional[str] = Field(None, alias="URL", description="원본 URL")
    keywords: Optional[str] = Field(None, alias="keywords", description="키워드 (문자열)")
    category: Optional[str] = Field(None, alias="category", description="카테고리")
    body: Optional[str] = Field(None, alias="body", description="본문")
    published_at: Optional[str] = Field(None, alias="published_at", description="발행일시 (문자열)")
    tags: List[str] = Field(default_factory=list, alias="tags", description="태그 목록")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "Title": "Google discontinues Clips, the AI-powered camera you forgot about",
                "Summary": "While Google was busy showcasing its latest devices yesterday...",
                "URL": "https://assets.msn.com/labs/mind/AAIT1gq.html",
                "keywords": "['latest devices yesterday', 'Google discontinues Clips']",
                "category": "Incidents & Safety",
                "body": "While Google was busy showcasing its latest devices yesterday...",
                "published_at": "2019-10-16 00:00:00",
                "tags": ["policy/Regulation", "topic/Safety", "geo/US"]
            }
        }
    }


class ArticleUpdateRequest(BaseModel):
    """Article 업데이트 요청 스키마"""
    title: Optional[str] = Field(None, alias="Title", min_length=1, max_length=500, description="기사 제목")
    summary: Optional[str] = Field(None, alias="Summary", description="기사 요약")
    url: Optional[str] = Field(None, alias="URL", description="원본 URL")
    keywords: Optional[str] = Field(None, alias="keywords", description="키워드 (문자열)")
    category: Optional[str] = Field(None, alias="category", description="카테고리")
    body: Optional[str] = Field(None, alias="body", description="본문")
    published_at: Optional[str] = Field(None, alias="published_at", description="발행일시 (문자열)")
    tags: Optional[List[str]] = Field(None, alias="tags", description="태그 목록")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "Title": "수정된 기사 제목",
                "Summary": "수정된 기사 요약...",
                "body": "수정된 본문 내용...",
                "tags": ["policy/Regulation", "topic/Safety", "geo/US", "업데이트"],
                "category": "Incidents & Safety"
            }
        }
    }


class ArticleListResponse(BaseModel):
    """Article 목록 응답 스키마"""
    items: List[ArticleResponse] = Field(..., description="기사 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "id": "68b97ad1e7c23a73720de215",
                        "Title": "Google discontinues Clips, the AI-powered camera you forgot about",
                        "Summary": "While Google was busy showcasing its latest devices yesterday...",
                        "URL": "https://assets.msn.com/labs/mind/AAIT1gq.html",
                        "keywords": "['latest devices yesterday', 'Google discontinues Clips']",
                        "category": "Incidents & Safety",
                        "body": "While Google was busy showcasing its latest devices yesterday...",
                        "published_at": "2019-10-16 00:00:00",
                        "tags": ["policy/Regulation", "topic/Safety", "geo/US"],
                        "updated_at": "2025-09-04 19:30:43",
                        "created_at": "2025-09-04 19:30:43"
                    }
                ],
                "total": 1,
                "page": 1,
                "size": 10
            }
        }
    }
