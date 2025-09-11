"""
모델 및 스키마 단위 테스트
"""

import pytest
from typing import List, Dict, Any
from pydantic import ValidationError

from src.redfin_api.models import (
    NewsEntry, NewsOut, HealthResponse, NewsQuery, NewsDescriptionResponse
)


class TestNewsEntry:
    """NewsEntry 모델 테스트"""

    def test_valid_news_entry(self):
        """유효한 NewsEntry 생성 테스트"""
        data = {
            "guid": "test-guid-123",
            "source": "Test Source",
            "title": "Test Title",
            "link": "https://example.com/news",
            "article_text": "Full article content here",
            "summary": "Brief summary",
            "tags": ["tag1", "tag2"],
            "content_type": "NEWS",
            "language": "ENGLISH",
            "readability_score": 8.5,
            "key_entities": ["Entity1", "Entity2"],
            "processed_at": "2024-01-01T12:00:00Z",
            "text_length": 100
        }
        news_entry = NewsEntry(**data)
        assert news_entry.guid == "test-guid-123"
        assert news_entry.source == "Test Source"
        assert news_entry.title == "Test Title"
        assert news_entry.content_type == "NEWS"
        assert news_entry.language == "ENGLISH"
        assert news_entry.readability_score == 8.5
        assert len(news_entry.tags) == 2
        assert len(news_entry.key_entities) == 2

    def test_news_entry_with_minimal_data(self):
        """최소 데이터로 NewsEntry 생성 테스트"""
        data = {
            "guid": "minimal-guid",
            "source": "Source",
            "title": "Title",
            "link": "https://example.com"
        }
        news_entry = NewsEntry(**data)
        assert news_entry.guid == "minimal-guid"
        assert news_entry.article_text is None
        assert news_entry.summary is None
        assert news_entry.tags == []
        assert news_entry.content_type == "NEWS"  # 기본값
        assert news_entry.language == "ENGLISH"  # 기본값
        assert news_entry.key_entities == []

    def test_news_entry_missing_required_fields(self):
        """필수 필드 누락 시 ValidationError 발생"""
        with pytest.raises(ValidationError) as exc_info:
            NewsEntry(source="Source", title="Title")  # guid, link 누락
        
        errors = exc_info.value.errors()
        missing_fields = {error['loc'][0] for error in errors}
        assert 'guid' in missing_fields
        assert 'link' in missing_fields

    def test_news_entry_invalid_types(self):
        """잘못된 타입으로 ValidationError 발생"""
        with pytest.raises(ValidationError):
            NewsEntry(
                guid=123,  # 문자열이어야 함
                source="Source",
                title="Title",
                link="https://example.com"
            )

    def test_news_entry_tags_validation(self):
        """태그 검증 테스트"""
        data = {
            "guid": "test-guid",
            "source": "Source",
            "title": "Title",
            "link": "https://example.com",
            "tags": ["tag1", "tag2", "tag3"]
        }
        news_entry = NewsEntry(**data)
        assert isinstance(news_entry.tags, list)
        assert all(isinstance(tag, str) for tag in news_entry.tags)


class TestNewsOut:
    """NewsOut 모델 테스트"""

    def test_valid_news_out(self):
        """유효한 NewsOut 생성 테스트"""
        data = {
            "source": "Test Source",
            "title": "Test Title",
            "link": "https://example.com/news",
            "published": "2024-01-01T12:00:00Z",
            "summary": "Test summary",
            "authors": ["Author 1", "Author 2"],
            "tags": ["tag1", "tag2"]
        }
        news_out = NewsOut(**data)
        assert news_out.source == "Test Source"
        assert news_out.title == "Test Title"
        assert str(news_out.link) == "https://example.com/news"
        assert news_out.published == "2024-01-01T12:00:00Z"
        assert len(news_out.authors) == 2
        assert len(news_out.tags) == 2

    def test_news_out_minimal_data(self):
        """최소 데이터로 NewsOut 생성 테스트"""
        data = {
            "link": "https://example.com"
        }
        news_out = NewsOut(**data)
        assert str(news_out.link) == "https://example.com"
        assert news_out.source is None
        assert news_out.title is None
        assert news_out.authors is None
        assert news_out.tags is None

    def test_news_out_invalid_url(self):
        """잘못된 URL로 ValidationError 발생"""
        with pytest.raises(ValidationError):
            NewsOut(link="not-a-valid-url")

    def test_news_out_missing_required_link(self):
        """필수 필드 link 누락 시 ValidationError 발생"""
        with pytest.raises(ValidationError) as exc_info:
            NewsOut(source="Source", title="Title")
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('link',) for error in errors)


class TestHealthResponse:
    """HealthResponse 모델 테스트"""

    def test_valid_health_response(self):
        """유효한 HealthResponse 생성 테스트"""
        data = {
            "ok": True,
            "count": 100,
            "backend": "FILE",
            "version": "0.1.0"
        }
        health = HealthResponse(**data)
        assert health.ok is True
        assert health.count == 100
        assert health.backend == "FILE"
        assert health.version == "0.1.0"

    def test_health_response_missing_fields(self):
        """필수 필드 누락 시 ValidationError 발생"""
        with pytest.raises(ValidationError):
            HealthResponse(ok=True, count=100)  # backend, version 누락


class TestNewsQuery:
    """NewsQuery 모델 테스트"""

    def test_valid_news_query(self):
        """유효한 NewsQuery 생성 테스트"""
        data = {
            "q": "test query",
            "source": "Test Source",
            "group": "Test Group",
            "limit": 50,
            "offset": 10,
            "sort": "fresh",
            "refresh": True
        }
        query = NewsQuery(**data)
        assert query.q == "test query"
        assert query.source == "Test Source"
        assert query.group == "Test Group"
        assert query.limit == 50
        assert query.offset == 10
        assert query.sort == "fresh"
        assert query.refresh is True

    def test_news_query_default_values(self):
        """기본값 테스트"""
        query = NewsQuery()
        assert query.q is None
        assert query.source is None
        assert query.group is None
        assert query.limit == 20
        assert query.offset == 0
        assert query.sort == "fresh"
        assert query.refresh is False

    def test_news_query_invalid_sort(self):
        """잘못된 sort 값으로 ValidationError 발생"""
        with pytest.raises(ValidationError):
            NewsQuery(sort="invalid_sort")

    def test_news_query_invalid_limit(self):
        """잘못된 limit 값으로 ValidationError 발생"""
        with pytest.raises(ValidationError):
            NewsQuery(limit=0)  # 최소값 1
        
        with pytest.raises(ValidationError):
            NewsQuery(limit=101)  # 최대값 100

    def test_news_query_invalid_offset(self):
        """잘못된 offset 값으로 ValidationError 발생"""
        with pytest.raises(ValidationError):
            NewsQuery(offset=-1)  # 최소값 0


class TestNewsDescriptionResponse:
    """NewsDescriptionResponse 모델 테스트"""

    def test_valid_news_description_response(self, sample_news_entries):
        """유효한 NewsDescriptionResponse 생성 테스트"""
        news_entries = [NewsEntry(**entry) for entry in sample_news_entries]
        
        data = {
            "success": True,
            "count": len(news_entries),
            "data": news_entries,
            "total": 100
        }
        response = NewsDescriptionResponse(**data)
        assert response.success is True
        assert response.count == len(news_entries)
        assert len(response.data) == len(news_entries)
        assert response.total == 100
        assert all(isinstance(entry, NewsEntry) for entry in response.data)

    def test_news_description_response_empty_data(self):
        """빈 데이터로 NewsDescriptionResponse 생성 테스트"""
        data = {
            "success": True,
            "count": 0,
            "data": [],
            "total": 0
        }
        response = NewsDescriptionResponse(**data)
        assert response.success is True
        assert response.count == 0
        assert len(response.data) == 0
        assert response.total == 0

    def test_news_description_response_missing_fields(self):
        """필수 필드 누락 시 ValidationError 발생"""
        with pytest.raises(ValidationError):
            NewsDescriptionResponse(success=True, count=0)  # data, total 누락


class TestModelIntegration:
    """모델 간 통합 테스트"""

    def test_news_entry_to_news_out_conversion(self, sample_news_entries):
        """NewsEntry에서 NewsOut으로 변환 테스트"""
        entry_data = sample_news_entries[0]
        news_entry = NewsEntry(**entry_data)
        
        # NewsEntry 데이터를 NewsOut 형태로 변환
        news_out_data = {
            "source": news_entry.source,
            "title": news_entry.title,
            "link": news_entry.link,
            "published": news_entry.processed_at,
            "summary": news_entry.summary,
            "tags": news_entry.tags
        }
        news_out = NewsOut(**news_out_data)
        
        assert news_out.source == news_entry.source
        assert news_out.title == news_entry.title
        assert str(news_out.link) == news_entry.link
        assert news_out.summary == news_entry.summary
        assert news_out.tags == news_entry.tags

    def test_complex_data_structures(self, sample_news_entries):
        """복잡한 데이터 구조 테스트"""
        # 여러 NewsEntry를 포함하는 NewsDescriptionResponse
        news_entries = [NewsEntry(**entry) for entry in sample_news_entries]
        
        response = NewsDescriptionResponse(
            success=True,
            count=len(news_entries),
            data=news_entries,
            total=len(news_entries)
        )
        
        # 응답 검증
        assert response.success is True
        assert response.count == len(sample_news_entries)
        assert len(response.data) == len(sample_news_entries)
        
        # 각 엔트리 검증
        for i, entry in enumerate(response.data):
            assert entry.guid == sample_news_entries[i]["guid"]
            assert entry.source == sample_news_entries[i]["source"]
            assert entry.title == sample_news_entries[i]["title"]
