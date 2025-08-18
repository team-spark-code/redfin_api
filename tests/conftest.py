"""
pytest 설정 파일
"""

import pytest
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def test_client():
    """테스트용 FastAPI 클라이언트"""
    from fastapi.testclient import TestClient
    from src.redfin_api.main import app
    return TestClient(app)

@pytest.fixture
def sample_news_data():
    """샘플 뉴스 데이터"""
    return [
        {
            "source": "Test Source",
            "title": "Test News Title",
            "link": "https://example.com/test-news",
            "published": "2024-01-01T12:00:00Z",
            "summary": "This is a test news summary",
            "authors": ["Test Author"],
            "tags": ["test", "news"]
        }
    ]
