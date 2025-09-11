"""
pytest 설정 파일 및 공통 픽스처
"""

import pytest
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


@pytest.fixture
def test_client():
    """테스트용 FastAPI 클라이언트"""
    from fastapi.testclient import TestClient
    from src.redfin_api.main import app
    return TestClient(app)


@pytest.fixture
def sample_news_data() -> List[Dict[str, Any]]:
    """샘플 뉴스 데이터 (NewsOut 모델용)"""
    return [
        {
            "source": "Test Source 1",
            "title": "Test News Title 1",
            "link": "https://example.com/test-news-1",
            "published": "2024-01-01T12:00:00Z",
            "summary": "This is a test news summary 1",
            "authors": ["Test Author 1"],
            "tags": ["test", "news", "ai"]
        },
        {
            "source": "Test Source 2",
            "title": "AI Revolution in Tech",
            "link": "https://example.com/ai-news",
            "published": "2024-01-02T10:30:00Z",
            "summary": "Artificial intelligence is changing the tech industry",
            "authors": ["AI Expert"],
            "tags": ["ai", "technology", "innovation"]
        },
        {
            "source": "Tech News",
            "title": "Python 3.12 Released",
            "link": "https://example.com/python-news",
            "published": "2024-01-03T14:15:00Z",
            "summary": "New features and improvements in Python 3.12",
            "authors": ["Python Team"],
            "tags": ["python", "programming", "release"]
        }
    ]


@pytest.fixture
def sample_news_entries() -> List[Dict[str, Any]]:
    """샘플 뉴스 엔트리 데이터 (NewsEntry 모델용)"""
    return [
        {
            "guid": "test-guid-1",
            "source": "Test Source 1",
            "title": "Test News Title 1",
            "link": "https://example.com/test-news-1",
            "article_text": "This is the full article text for test news 1. It contains detailed information about the topic.",
            "summary": "This is a test news summary 1",
            "tags": ["test", "news", "ai"],
            "content_type": "NEWS",
            "language": "ENGLISH",
            "readability_score": 8.5,
            "key_entities": ["AI", "Technology", "Innovation"],
            "processed_at": "2024-01-01T12:00:00Z",
            "text_length": 150
        },
        {
            "guid": "test-guid-2",
            "source": "AI Research",
            "title": "Machine Learning Breakthrough",
            "link": "https://example.com/ml-breakthrough",
            "article_text": "Researchers have achieved a significant breakthrough in machine learning algorithms.",
            "summary": "New ML algorithm shows 95% accuracy",
            "tags": ["machine-learning", "research", "breakthrough"],
            "content_type": "RESEARCH",
            "language": "ENGLISH",
            "readability_score": 7.2,
            "key_entities": ["Machine Learning", "Algorithm", "Research"],
            "processed_at": "2024-01-02T09:45:00Z",
            "text_length": 200
        }
    ]


@pytest.fixture
def mock_file_data(sample_news_entries):
    """파일 로딩을 위한 모킹된 데이터"""
    return sample_news_entries


@pytest.fixture
def mock_mongo_data(sample_news_entries):
    """MongoDB 로딩을 위한 모킹된 데이터"""
    return sample_news_entries


@pytest.fixture
def mock_load_file(mock_file_data):
    """_load_file 함수 모킹"""
    with patch('src.redfin_api.main._load_file', return_value=mock_file_data) as mock:
        yield mock


@pytest.fixture
def mock_load_mongo(mock_mongo_data):
    """_load_mongo 함수 모킹"""
    with patch('src.redfin_api.main._load_mongo', return_value=mock_mongo_data) as mock:
        yield mock


@pytest.fixture
def mock_load_data(mock_file_data):
    """_load_data 함수 모킹"""
    with patch('src.redfin_api.main._load_data', return_value=mock_file_data) as mock:
        yield mock


@pytest.fixture
def mock_news_cache(mock_file_data):
    """뉴스 캐시 모킹"""
    with patch('src.redfin_api.main._news_cache', mock_file_data):
        yield mock_file_data


@pytest.fixture
def empty_news_cache():
    """빈 뉴스 캐시"""
    with patch('src.redfin_api.main._news_cache', []):
        yield []


@pytest.fixture
def mock_config_file_backend():
    """파일 백엔드 설정 모킹"""
    with patch('src.redfin_api.config.BACKEND', 'FILE'):
        yield


@pytest.fixture
def mock_config_mongo_backend():
    """MongoDB 백엔드 설정 모킹"""
    with patch('src.redfin_api.config.BACKEND', 'MONGO'), \
         patch('src.redfin_api.config.MONGO_URI', 'mongodb://localhost:27017'):
        yield


@pytest.fixture
def mock_pymongo():
    """PyMongo 모킹"""
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_client.__getitem__.return_value.__getitem__.return_value = mock_collection
    
    with patch('pymongo.MongoClient', return_value=mock_client) as mock:
        yield mock, mock_collection


@pytest.fixture
def test_json_file(tmp_path, sample_news_entries):
    """테스트용 임시 JSON 파일"""
    test_file = tmp_path / "test_news.json"
    with test_file.open("w", encoding="utf-8") as f:
        json.dump(sample_news_entries, f)
    return test_file


@pytest.fixture
def test_jsonl_file(tmp_path, sample_news_entries):
    """테스트용 임시 JSONL 파일"""
    test_file = tmp_path / "test_news.jsonl"
    with test_file.open("w", encoding="utf-8") as f:
        for entry in sample_news_entries:
            json.dump(entry, f)
            f.write("\n")
    return test_file


@pytest.fixture
def invalid_json_file(tmp_path):
    """잘못된 JSON 파일"""
    test_file = tmp_path / "invalid.json"
    with test_file.open("w", encoding="utf-8") as f:
        f.write('{"invalid": json content')
    return test_file


@pytest.fixture
def setup_test_environment():
    """테스트 환경 설정"""
    # 테스트 중 로그 레벨 조정
    import logging
    logging.getLogger('src.redfin_api.main').setLevel(logging.CRITICAL)
    yield
    # 테스트 후 정리
    logging.getLogger('src.redfin_api.main').setLevel(logging.INFO)