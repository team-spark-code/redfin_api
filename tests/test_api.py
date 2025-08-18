"""
RedFin API 테스트
"""

import pytest
from fastapi.testclient import TestClient
from src.redfin_api.main import app

client = TestClient(app)

def test_health_endpoint():
    """헬스체크 엔드포인트 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "count" in data
    assert "backend" in data
    assert "version" in data

def test_sources_endpoint():
    """소스 목록 엔드포인트 테스트"""
    response = client.get("/sources")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_news_endpoint():
    """뉴스 목록 엔드포인트 테스트"""
    response = client.get("/news")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_news_with_query_params():
    """쿼리 파라미터가 있는 뉴스 엔드포인트 테스트"""
    response = client.get("/news?limit=5&offset=0&sort=fresh")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5

def test_news_search():
    """뉴스 검색 테스트"""
    response = client.get("/news?q=test")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_news_source_filter():
    """소스 필터 테스트"""
    response = client.get("/news?source=test_source")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_invalid_sort_parameter():
    """잘못된 정렬 파라미터 테스트"""
    response = client.get("/news?sort=invalid")
    assert response.status_code == 422  # Validation error

def test_invalid_limit_parameter():
    """잘못된 limit 파라미터 테스트"""
    response = client.get("/news?limit=0")
    assert response.status_code == 422  # Validation error

def test_invalid_offset_parameter():
    """잘못된 offset 파라미터 테스트"""
    response = client.get("/news?offset=-1")
    assert response.status_code == 422  # Validation error
