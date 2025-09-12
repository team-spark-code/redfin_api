"""
Article 스키마 정의 (API 요청/응답)
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class ArticleCategory(str, Enum):
    """기사 카테고리 열거형"""
    RESEARCH = "Research"
    TECHNOLOGY_PRODUCT = "Technology & Product"
    MARKET_CORPORATE = "Market & Corporate"
    POLICY_REGULATION = "Policy & Regulation"
    SOCIAL_DISCUSSION = "Social Discussion"
    INCIDENTS_SAFETY = "Incidents & Safety"
    MISC = "Misc"


# 카테고리 상수 정의
ARTICLE_CATEGORIES = {
    "Research": {
        "name": "Research",
        "name_ko": "학술",
        "description": "논문, 프리프린트, 학술 성과, 벤치마크/데이터셋",
        "condition": "핵심 메시지가 연구 결과일 때"
    },
    "Technology & Product": {
        "name": "Technology & Product", 
        "name_ko": "기술/제품",
        "description": "모델 제품 출시, 성능 업데이트, 기능 변경",
        "condition": "제품/기능 제공이 핵심일 때"
    },
    "Market & Corporate": {
        "name": "Market & Corporate",
        "name_ko": "시장/기업", 
        "description": "투자, M&A, IPO, 실적, 조직 개편, 파트너십/상용화",
        "condition": "금융 거래와 지배구조가 중심일 때"
    },
    "Policy & Regulation": {
        "name": "Policy & Regulation",
        "name_ko": "정책/규제",
        "description": "법률/규정/가이드라인, 보조금, 수출/통제, 표준화",
        "condition": "공공기관의 규제/지원이 핵심일 때"
    },
    "Social Discussion": {
        "name": "Social Discussion",
        "name_ko": "사회적 논의",
        "description": "공공 활용, 창작/교육, 밈, 사회적 논의 (정책 이전 단계)",
        "condition": "사회적 확산과 수용이 중심일 때"
    },
    "Incidents & Safety": {
        "name": "Incidents & Safety",
        "name_ko": "사건/안전/운영",
        "description": "서비스 장애, 보안 사고, 오남용, 리콜/중단",
        "condition": "사고나 안전 관련 이슈일 때"
    },
    "Misc": {
        "name": "Misc",
        "name_ko": "기타",
        "description": "위 카테고리에 속하지 않는 기타 내용",
        "condition": "분류가 어려운 기사일 때"
    }
}


class ArticleResponse(BaseModel):
    """Article 응답 스키마"""
    id: str = Field(..., description="기사 ID")
    title: str = Field(..., description="기사 제목")
    summary: Optional[str] = Field(None, description="기사 요약")
    url: Optional[str] = Field(None, description="원본 URL")
    keywords: List[str] = Field(default_factory=list, description="키워드 목록")
    category: Optional[str] = Field(None, description="카테고리")
    body: Optional[str] = Field(None, description="본문")
    published_at: Optional[str] = Field(None, description="발행일시 (문자열)")
    tags: List[str] = Field(default_factory=list, description="태그 목록")
    updated_at: Optional[str] = Field(None, description="수정일시")
    created_at: Optional[str] = Field(None, description="생성일시")
    hero_image_url: Optional[str] = Field(None, description="대표 이미지 URL")
    author_name: Optional[str] = Field(None, description="작성자명")
    sources: List[str] = Field(default_factory=list, description="출처 목록")
    
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


class CategoryInfo(BaseModel):
    """카테고리 정보 스키마"""
    name: str = Field(..., description="카테고리명 (영문)")
    name_ko: str = Field(..., description="카테고리명 (한글)")
    description: str = Field(..., description="카테고리 설명")
    condition: str = Field(..., description="카테고리 적용 조건")
    count: Optional[int] = Field(None, description="해당 카테고리 기사 수")


class CategoryListResponse(BaseModel):
    """카테고리 목록 응답 스키마"""
    categories: List[CategoryInfo] = Field(..., description="카테고리 목록")
    total: int = Field(..., description="전체 카테고리 수")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "categories": [
                    {
                        "name": "Research",
                        "name_ko": "학술",
                        "description": "논문, 프리프린트, 학술 성과, 벤치마크/데이터셋",
                        "condition": "핵심 메시지가 연구 결과일 때",
                        "count": 15
                    },
                    {
                        "name": "Technology & Product",
                        "name_ko": "기술/제품",
                        "description": "모델 제품 출시, 성능 업데이트, 기능 변경",
                        "condition": "제품/기능 제공이 핵심일 때",
                        "count": 23
                    }
                ],
                "total": 7
            }
        }
    }
