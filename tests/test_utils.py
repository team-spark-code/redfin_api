"""
유틸리티 함수 단위 테스트
"""

import pytest
import time
from datetime import datetime
from unittest.mock import patch

from src.redfin_api.main import (
    _freshness_score, _normalize_news_item, _load_file, _load_mongo, _load_data
)


class TestFreshnessScore:
    """_freshness_score 함수 테스트"""

    def test_freshness_score_with_published(self):
        """published 필드가 있는 경우 신선도 점수 계산"""
        now_ts = time.time()
        item = {
            "published": "Mon, 25 Aug 2025 06:00:00 GMT"
        }
        
        score = _freshness_score(item, now_ts)
        assert isinstance(score, float)
        assert score >= 0.0

    def test_freshness_score_with_processed_at(self):
        """processed_at 필드가 있는 경우 신선도 점수 계산"""
        now_ts = time.time()
        item = {
            "processed_at": "2025-08-26T11:47:10.173932"
        }
        
        score = _freshness_score(item, now_ts)
        assert isinstance(score, float)
        assert score >= 0.0

    def test_freshness_score_iso_format(self):
        """ISO 형식 날짜의 신선도 점수 계산"""
        now_ts = time.time()
        item = {
            "published": "2025-08-26T11:47:10Z"
        }
        
        score = _freshness_score(item, now_ts)
        assert isinstance(score, float)
        assert score >= 0.0

    def test_freshness_score_no_date(self):
        """날짜 정보가 없는 경우"""
        now_ts = time.time()
        item = {
            "title": "News without date"
        }
        
        score = _freshness_score(item, now_ts)
        assert score == 0.0

    def test_freshness_score_invalid_date(self):
        """잘못된 날짜 형식인 경우"""
        now_ts = time.time()
        item = {
            "published": "invalid date format"
        }
        
        score = _freshness_score(item, now_ts)
        assert score == 0.0

    def test_freshness_score_recent_vs_old(self):
        """최근 뉴스와 오래된 뉴스의 점수 비교"""
        now_ts = time.time()
        
        # 1시간 전 뉴스
        recent_item = {
            "published": datetime.fromtimestamp(now_ts - 3600).isoformat()
        }
        
        # 24시간 전 뉴스
        old_item = {
            "published": datetime.fromtimestamp(now_ts - 86400).isoformat()
        }
        
        recent_score = _freshness_score(recent_item, now_ts)
        old_score = _freshness_score(old_item, now_ts)
        
        # 최근 뉴스의 점수가 더 높아야 함
        assert recent_score > old_score

    def test_freshness_score_edge_cases(self):
        """경계 케이스 테스트"""
        now_ts = time.time()
        
        # 빈 문자열
        empty_item = {"published": ""}
        assert _freshness_score(empty_item, now_ts) == 0.0
        
        # None 값
        none_item = {"published": None}
        assert _freshness_score(none_item, now_ts) == 0.0
        
        # 미래 날짜 (음수 age 방지)
        future_item = {
            "published": datetime.fromtimestamp(now_ts + 3600).isoformat()
        }
        score = _freshness_score(future_item, now_ts)
        assert score >= 0.0


class TestNormalizeNewsItem:
    """_normalize_news_item 함수 테스트"""

    def test_normalize_extract_structure(self):
        """extract_20250826_105701.json 구조 정규화"""
        item = {
            "guid": "test-guid",
            "source": "Test Source",
            "title": "Test Title",
            "link": "https://example.com",
            "article_text": "Article content",
            "summary": "Summary",
            "tags": ["tag1", "tag2"],
            "content_type": "NEWS",
            "language": "ENGLISH",
            "readability_score": 8.5,
            "key_entities": ["Entity1"],
            "processed_at": "2024-01-01T12:00:00Z",
            "text_length": 100
        }
        
        normalized = _normalize_news_item(item)
        
        assert normalized["guid"] == "test-guid"
        assert normalized["source"] == "Test Source"
        assert normalized["title"] == "Test Title"
        assert normalized["link"] == "https://example.com"
        assert normalized["article_text"] == "Article content"
        assert normalized["summary"] == "Summary"
        assert normalized["tags"] == ["tag1", "tag2"]
        assert normalized["content_type"] == "NEWS"
        assert normalized["language"] == "ENGLISH"
        assert normalized["readability_score"] == 8.5
        assert normalized["key_entities"] == ["Entity1"]
        assert normalized["processed_at"] == "2024-01-01T12:00:00Z"
        assert normalized["text_length"] == 100

    def test_normalize_simple_structure(self):
        """간단한 구조 정규화"""
        item = {
            "type": "news",
            "source": "Simple Source",
            "title": "Simple Title",
            "link": "https://example.com/simple",
            "summary": "Simple summary",
            "published": "2024-01-01T12:00:00Z",
            "tags": ["simple"]
        }
        
        normalized = _normalize_news_item(item)
        
        assert normalized["guid"] == "https://example.com/simple"  # link가 ID로 사용
        assert normalized["source"] == "Simple Source"
        assert normalized["title"] == "Simple Title"
        assert normalized["link"] == "https://example.com/simple"
        assert normalized["article_text"] == "Simple summary"  # summary가 article_text로 사용
        assert normalized["summary"] == "Simple summary"
        assert normalized["tags"] == ["simple"]
        assert normalized["content_type"] == "NEWS"
        assert normalized["language"] == "ENGLISH"
        assert normalized["readability_score"] is None
        assert normalized["key_entities"] == []
        assert normalized["processed_at"] == "2024-01-01T12:00:00Z"
        assert normalized["text_length"] == len("Simple summary")

    def test_normalize_existing_detailed_structure(self):
        """기존 상세 구조 정규화"""
        item = {
            "guid": "detailed-guid",
            "source": "Detailed Source",
            "title": "Detailed Title",
            "link": "https://example.com/detailed",
            "article_text": "Detailed article",
            "summary": "Detailed summary",
            "tags": ["detailed", "news"],
            "content_type": "ARTICLE",
            "language": "KOREAN",
            "readability_score": 7.2,
            "key_entities": ["Korea", "News"],
            "processed_at": "2024-01-02T10:00:00Z",
            "text_length": 200
        }
        
        normalized = _normalize_news_item(item)
        
        # 모든 필드가 그대로 유지되어야 함
        assert normalized["guid"] == "detailed-guid"
        assert normalized["content_type"] == "ARTICLE"
        assert normalized["language"] == "KOREAN"
        assert normalized["readability_score"] == 7.2
        assert normalized["key_entities"] == ["Korea", "News"]

    def test_normalize_missing_fields(self):
        """필드가 누락된 경우 기본값 적용"""
        item = {
            "guid": "minimal-guid",
            "source": "Minimal Source",
            "title": "Minimal Title",
            "link": "https://example.com/minimal"
        }
        
        normalized = _normalize_news_item(item)
        
        assert normalized["guid"] == "minimal-guid"
        assert normalized["article_text"] is None
        assert normalized["summary"] is None
        assert normalized["tags"] == []
        assert normalized["content_type"] == "NEWS"
        assert normalized["language"] == "ENGLISH"
        assert normalized["readability_score"] is None
        assert normalized["key_entities"] == []
        assert normalized["processed_at"] is None
        assert normalized["text_length"] is None

    def test_normalize_empty_values(self):
        """빈 값들의 처리"""
        item = {
            "guid": "",
            "source": "",
            "title": "",
            "link": "",
            "article_text": "",
            "summary": "",
            "tags": [],
            "key_entities": []
        }
        
        normalized = _normalize_news_item(item)
        
        assert normalized["guid"] == ""
        assert normalized["source"] == ""
        assert normalized["title"] == ""
        assert normalized["link"] == ""
        assert normalized["article_text"] == ""
        assert normalized["summary"] == ""
        assert normalized["tags"] == []
        assert normalized["key_entities"] == []


class TestLoadFile:
    """_load_file 함수 테스트"""

    @patch('src.redfin_api.main.Path.exists')
    @patch('src.redfin_api.main.Path.open')
    @patch('src.redfin_api.main.json.load')
    def test_load_file_success(self, mock_json_load, mock_open, mock_exists):
        """파일 로딩 성공 테스트"""
        mock_exists.return_value = True
        mock_json_load.return_value = [{"test": "data"}]
        
        result = _load_file()
        
        assert result == [{"test": "data"}]
        mock_exists.assert_called()
        mock_open.assert_called()
        mock_json_load.assert_called()

    @patch('src.redfin_api.main.Path.exists')
    def test_load_file_not_exists(self, mock_exists):
        """파일이 존재하지 않는 경우"""
        mock_exists.return_value = False
        
        result = _load_file()
        
        assert result == []

    @patch('src.redfin_api.main.Path.exists')
    @patch('src.redfin_api.main.Path.open')
    def test_load_file_json_error(self, mock_open, mock_exists):
        """JSON 파싱 오류"""
        mock_exists.return_value = True
        mock_open.side_effect = Exception("File error")
        
        result = _load_file()
        
        assert result == []


class TestLoadMongo:
    """_load_mongo 함수 테스트"""

    @patch('src.redfin_api.main.MONGO_URI', 'mongodb://test:27017')
    @patch('pymongo.MongoClient')
    def test_load_mongo_success(self, mock_client):
        """MongoDB 로딩 성공 테스트"""
        mock_collection = mock_client.return_value.__getitem__.return_value.__getitem__.return_value
        mock_collection.find.return_value.sort.return_value = [{"test": "data"}]
        
        result = _load_mongo()
        
        assert result == [{"test": "data"}]
        mock_client.assert_called_with('mongodb://test:27017')

    @patch('src.redfin_api.main.MONGO_URI', None)
    def test_load_mongo_no_uri(self):
        """MongoDB URI가 없는 경우"""
        result = _load_mongo()
        assert result == []

    @patch('src.redfin_api.main.MONGO_URI', 'mongodb://test:27017')
    @patch('pymongo.MongoClient')
    def test_load_mongo_connection_error(self, mock_client):
        """MongoDB 연결 오류"""
        mock_client.side_effect = Exception("Connection error")
        
        result = _load_mongo()
        
        assert result == []


class TestLoadData:
    """_load_data 함수 테스트"""

    @patch('src.redfin_api.main.BACKEND', 'MONGO')
    @patch('src.redfin_api.main.MONGO_URI', 'mongodb://test:27017')
    @patch('src.redfin_api.main._load_mongo')
    def test_load_data_mongo_backend(self, mock_load_mongo):
        """MongoDB 백엔드로 데이터 로딩"""
        mock_load_mongo.return_value = [{"mongo": "data"}]
        
        result = _load_data()
        
        assert result == [{"mongo": "data"}]
        mock_load_mongo.assert_called_once()

    @patch('src.redfin_api.main.BACKEND', 'FILE')
    @patch('src.redfin_api.main._load_file')
    def test_load_data_file_backend(self, mock_load_file):
        """파일 백엔드로 데이터 로딩"""
        mock_load_file.return_value = [{"file": "data"}]
        
        result = _load_data()
        
        assert result == [{"file": "data"}]
        mock_load_file.assert_called_once()

    @patch('src.redfin_api.main.BACKEND', 'MONGO')
    @patch('src.redfin_api.main.MONGO_URI', None)
    @patch('src.redfin_api.main._load_file')
    def test_load_data_fallback_to_file(self, mock_load_file):
        """MongoDB 설정이 없어 파일로 폴백"""
        mock_load_file.return_value = [{"fallback": "data"}]
        
        result = _load_data()
        
        assert result == [{"fallback": "data"}]
        mock_load_file.assert_called_once()


class TestUtilityIntegration:
    """유틸리티 함수 통합 테스트"""

    def test_freshness_score_and_normalize_integration(self):
        """신선도 점수와 정규화 함수 통합 테스트"""
        now_ts = time.time()
        
        # 다양한 구조의 뉴스 아이템들
        items = [
            {
                "guid": "guid1",
                "source": "Source1",
                "title": "Title1",
                "link": "https://example.com/1",
                "processed_at": datetime.fromtimestamp(now_ts - 3600).isoformat()
            },
            {
                "type": "news",
                "source": "Source2",
                "title": "Title2",
                "link": "https://example.com/2",
                "published": datetime.fromtimestamp(now_ts - 7200).isoformat()
            }
        ]
        
        # 정규화 후 신선도 점수 계산
        normalized_items = [_normalize_news_item(item) for item in items]
        scores = [_freshness_score(item, now_ts) for item in normalized_items]
        
        # 첫 번째 아이템(더 최근)의 점수가 더 높아야 함
        assert len(scores) == 2
        assert scores[0] > scores[1]

    def test_data_loading_and_normalization_flow(self):
        """데이터 로딩과 정규화 전체 플로우 테스트"""
        sample_data = [
            {
                "guid": "flow-test",
                "source": "Flow Source",
                "title": "Flow Title",
                "link": "https://example.com/flow",
                "summary": "Flow summary"
            }
        ]
        
        with patch('src.redfin_api.main._load_file', return_value=sample_data):
            # 데이터 로딩
            loaded_data = _load_data()
            
            # 정규화
            normalized_data = [_normalize_news_item(item) for item in loaded_data]
            
            # 신선도 점수 계산
            now_ts = time.time()
            scores = [_freshness_score(item, now_ts) for item in normalized_data]
            
            assert len(loaded_data) == 1
            assert len(normalized_data) == 1
            assert len(scores) == 1
            assert normalized_data[0]["guid"] == "flow-test"
            assert isinstance(scores[0], float)
