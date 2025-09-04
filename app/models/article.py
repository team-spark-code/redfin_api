"""
Article 모델 정의
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """MongoDB ObjectId를 Pydantic과 호환되도록 하는 클래스"""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
        raise ValueError("Invalid ObjectId")
    
    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler):
        return {"type": "string"}


class ArticleBase(BaseModel):
    """Article 기본 모델"""
    title: str = Field(..., alias="Title", description="기사 제목")
    summary: Optional[str] = Field(None, alias="Summary", description="기사 요약")
    url: Optional[str] = Field(None, alias="URL", description="원본 URL")
    keywords: Optional[str] = Field(None, alias="keywords", description="키워드 (문자열)")
    category: Optional[str] = Field(None, alias="category", description="카테고리")
    body: Optional[str] = Field(None, alias="body", description="본문")
    published_at: Optional[str] = Field(None, alias="published_at", description="발행일시 (문자열)")
    tags: list[str] = Field(default_factory=list, alias="tags", description="태그 목록")
    updated_at: Optional[str] = Field(None, alias="updated_at", description="수정일시")
    created_at: Optional[str] = Field(None, alias="created_at", description="생성일시")


class ArticleCreate(ArticleBase):
    """Article 생성 모델"""
    pass


class ArticleUpdate(BaseModel):
    """Article 업데이트 모델"""
    title: Optional[str] = Field(None, alias="Title")
    summary: Optional[str] = Field(None, alias="Summary")
    url: Optional[str] = Field(None, alias="URL")
    keywords: Optional[str] = Field(None, alias="keywords")
    category: Optional[str] = Field(None, alias="category")
    body: Optional[str] = Field(None, alias="body")
    published_at: Optional[str] = Field(None, alias="published_at")
    tags: Optional[list[str]] = Field(None, alias="tags")
    updated_at: Optional[str] = Field(None, alias="updated_at")


class Article(ArticleBase):
    """Article 응답 모델"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "json_schema_extra": {
            "example": {
                "_id": "68b97ad1e7c23a73720de215",
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
