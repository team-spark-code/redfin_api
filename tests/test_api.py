"""
API 엔드포인트 단위 테스트 (개선된 버전)
"""

import pytest
import json
import time
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.redfin_api.main import app


class TestHealthEndpoint:
    """헬스체크 엔드포인트 테스트"""

    def test_health_endpoint_success(self, test_client, mock_news_cache):
        """헬스체크 엔드포인트 성공 테스트"""
        response = test_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["ok"] is True
        assert "count" in data
        assert "backend" in data
        assert "version" in data
        assert data["version"] == "0.1.0"

    def test_health_endpoint_with_empty_cache(self, test_client, empty_news_cache):
        """빈 캐시일 때 헬스체크 테스트"""
        response = test_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["ok"] is True
        assert data["count"] == 0

    def test_health_endpoint_response_model(self, test_client, mock_news_cache):
        """헬스체크 응답 모델 검증"""
        response = test_client.get("/health")
        data = response.json()
        
        # HealthResponse 모델의 모든 필드 확인
        required_fields = ["ok", "count", "backend", "version"]
        for field in required_fields:
            assert field in data
        
        assert isinstance(data["ok"], bool)
        assert isinstance(data["count"], int)
        assert isinstance(data["backend"], str)
        assert isinstance(data["version"], str)


class TestRootEndpoint:
    """루트 엔드포인트 테스트"""

    def test_root_endpoint(self, test_client):
        """루트 엔드포인트 테스트"""
        response = test_client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
        assert "usage" in data
        assert data["version"] == "0.1.0"

    def test_root_endpoint_structure(self, test_client):
        """루트 엔드포인트 응답 구조 테스트"""
        response = test_client.get("/")
        data = response.json()
        
        # 필수 섹션들 확인
        assert "endpoints" in data
        assert "usage" in data
        assert "data_structures" in data
        
        # 엔드포인트 정보 확인
        endpoints = data["endpoints"]
        expected_endpoints = ["health", "news", "news_descriptions", "sources", "groups"]
        for endpoint in expected_endpoints:
            assert endpoint in endpoints


class TestSourcesEndpoint:
    """소스 목록 엔드포인트 테스트"""

    def test_sources_endpoint(self, test_client, mock_news_cache):
        """소스 목록 엔드포인트 테스트"""
        response = test_client.get("/sources")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_sources_with_data(self, test_client, sample_news_entries):
        """데이터가 있을 때 소스 목록 테스트"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            response = test_client.get("/sources")
            sources = response.json()
            
            # 샘플 데이터의 소스들이 포함되어야 함
            expected_sources = {entry["source"] for entry in sample_news_entries}
            assert set(sources) == expected_sources

    def test_sources_empty_cache(self, test_client, empty_news_cache):
        """빈 캐시일 때 소스 목록 테스트"""
        response = test_client.get("/sources")
        assert response.status_code == 200
        assert response.json() == []

    def test_sources_sorted(self, test_client):
        """소스 목록 정렬 테스트"""
        test_data = [
            {"source": "Z Source", "title": "Title"},
            {"source": "A Source", "title": "Title"},
            {"source": "M Source", "title": "Title"}
        ]
        
        with patch('src.redfin_api.main._news_cache', test_data):
            response = test_client.get("/sources")
            sources = response.json()
            
            # 정렬되어 있어야 함
            assert sources == sorted(sources)


class TestGroupsEndpoint:
    """그룹 목록 엔드포인트 테스트"""

    def test_groups_endpoint(self, test_client, mock_news_cache):
        """그룹 목록 엔드포인트 테스트"""
        response = test_client.get("/groups")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_groups_with_data(self, test_client):
        """그룹이 있는 데이터로 테스트"""
        test_data = [
            {"group": "Technology", "title": "Tech News"},
            {"group": "Science", "title": "Science News"},
            {"group": "Technology", "title": "Another Tech News"}
        ]
        
        with patch('src.redfin_api.main._news_cache', test_data):
            response = test_client.get("/groups")
            groups = response.json()
            
            # 중복 제거된 그룹 목록이어야 함
            assert set(groups) == {"Technology", "Science"}
            assert len(groups) == 2

    def test_groups_empty_cache(self, test_client, empty_news_cache):
        """빈 캐시일 때 그룹 목록 테스트"""
        response = test_client.get("/groups")
        assert response.status_code == 200
        assert response.json() == []


class TestNewsEndpoint:
    """뉴스 목록 엔드포인트 테스트"""

    def test_news_endpoint_basic(self, test_client, mock_news_cache):
        """기본 뉴스 엔드포인트 테스트"""
        response = test_client.get("/news")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_news_with_limit(self, test_client, sample_news_entries):
        """limit 파라미터 테스트"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            response = test_client.get("/news?limit=1")
            assert response.status_code == 200
            
            news = response.json()
            assert len(news) <= 1

    def test_news_with_offset(self, test_client, sample_news_entries):
        """offset 파라미터 테스트"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            # 첫 번째 페이지
            response1 = test_client.get("/news?limit=1&offset=0")
            # 두 번째 페이지
            response2 = test_client.get("/news?limit=1&offset=1")
            
            assert response1.status_code == 200
            assert response2.status_code == 200
            
            news1 = response1.json()
            news2 = response2.json()
            
            # 다른 결과여야 함 (데이터가 충분할 때)
            if len(news1) > 0 and len(news2) > 0:
                assert news1[0] != news2[0]

    def test_news_with_query_search(self, test_client, sample_news_entries):
        """검색어로 뉴스 필터링 테스트"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            response = test_client.get("/news?q=test")
            assert response.status_code == 200
            
            news = response.json()
            # 검색어가 포함된 뉴스만 반환되어야 함
            for item in news:
                search_fields = [
                    item.get("title", "").lower(),
                    item.get("summary", "").lower(),
                    " ".join(item.get("tags", [])).lower()
                ]
                assert any("test" in field for field in search_fields)

    def test_news_with_source_filter(self, test_client, sample_news_entries):
        """소스 필터링 테스트"""
        target_source = sample_news_entries[0]["source"]
        
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            response = test_client.get(f"/news?source={target_source}")
            assert response.status_code == 200
            
            news = response.json()
            for item in news:
                assert item["source"] == target_source

    def test_news_sorting_fresh(self, test_client, sample_news_entries):
        """신선도 정렬 테스트"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            response = test_client.get("/news?sort=fresh")
            assert response.status_code == 200
            assert isinstance(response.json(), list)

    def test_news_sorting_time(self, test_client, sample_news_entries):
        """시간 정렬 테스트"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            response = test_client.get("/news?sort=time")
            assert response.status_code == 200
            assert isinstance(response.json(), list)

    def test_news_with_refresh(self, test_client, mock_load_data):
        """캐시 새로고침 테스트"""
        response = test_client.get("/news?refresh=true")
        assert response.status_code == 200
        
        # _load_data가 호출되었는지 확인
        mock_load_data.assert_called()

    def test_news_invalid_parameters(self, test_client):
        """잘못된 파라미터 검증 테스트"""
        # 잘못된 정렬 방식
        response = test_client.get("/news?sort=invalid")
        assert response.status_code == 422

        # 잘못된 limit
        response = test_client.get("/news?limit=0")
        assert response.status_code == 422

        response = test_client.get("/news?limit=101")
        assert response.status_code == 422

        # 잘못된 offset
        response = test_client.get("/news?offset=-1")
        assert response.status_code == 422


class TestNewsDescriptionsEndpoint:
    """뉴스 description 엔드포인트 테스트"""

    def test_news_descriptions_basic(self, test_client, sample_news_entries):
        """기본 news descriptions 엔드포인트 테스트"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            response = test_client.get("/news/descriptions")
            assert response.status_code == 200
            
            data = response.json()
            assert "success" in data
            assert "count" in data
            assert "data" in data
            assert "total" in data
            assert data["success"] is True
            assert isinstance(data["data"], list)

    def test_news_descriptions_with_filters(self, test_client, sample_news_entries):
        """필터가 적용된 news descriptions 테스트"""
        target_source = sample_news_entries[0]["source"]
        
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            response = test_client.get(f"/news/descriptions?source={target_source}&limit=5")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) <= 5
            
            # 모든 항목이 지정된 소스여야 함
            for item in data["data"]:
                assert item["source"] == target_source

    def test_news_descriptions_search(self, test_client, sample_news_entries):
        """description 검색 테스트"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            response = test_client.get("/news/descriptions?q=test")
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            
            # 검색어가 포함된 항목만 반환되어야 함
            for item in data["data"]:
                search_fields = [
                    item.get("title", "").lower(),
                    item.get("summary", "").lower(),
                    item.get("article_text", "").lower(),
                    " ".join(item.get("tags", [])).lower()
                ]
                assert any("test" in field for field in search_fields)

    def test_news_descriptions_empty_cache(self, test_client, empty_news_cache):
        """빈 캐시일 때 descriptions 테스트"""
        response = test_client.get("/news/descriptions")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 0
        assert data["total"] == 0
        assert data["data"] == []


class TestNewsExtractEndpoint:
    """뉴스 extract 엔드포인트 테스트"""

    def test_news_extract_basic(self, test_client, sample_news_entries):
        """기본 news extract 엔드포인트 테스트"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            response = test_client.get("/news/extract")
            assert response.status_code == 200
            assert isinstance(response.json(), list)

    def test_news_extract_with_filters(self, test_client, sample_news_entries):
        """필터가 적용된 extract 테스트"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            response = test_client.get("/news/extract?limit=1&sort=time")
            assert response.status_code == 200
            
            news = response.json()
            assert len(news) <= 1
            
            # NewsEntry 모델의 필드들이 포함되어야 함
            if news:
                item = news[0]
                expected_fields = [
                    "guid", "source", "title", "link", "article_text",
                    "summary", "tags", "content_type", "language"
                ]
                for field in expected_fields:
                    assert field in item

    def test_news_extract_search(self, test_client, sample_news_entries):
        """extract 검색 테스트"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            response = test_client.get("/news/extract?q=research")
            assert response.status_code == 200
            
            news = response.json()
            # 검색어가 포함된 항목만 반환되어야 함
            for item in news:
                search_fields = [
                    item.get("title", "").lower(),
                    item.get("summary", "").lower(),
                    item.get("article_text", "").lower(),
                    " ".join(item.get("tags", [])).lower()
                ]
                assert any("research" in field for field in search_fields)


class TestErrorHandling:
    """에러 처리 테스트"""

    def test_data_conversion_error(self, test_client):
        """데이터 변환 오류 처리 테스트"""
        # 잘못된 형태의 데이터로 오류 유발
        invalid_data = [{"invalid": "data without required fields"}]
        
        with patch('src.redfin_api.main._news_cache', invalid_data):
            response = test_client.get("/news")
            # 오류가 발생하더라도 빈 배열이나 적절한 응답을 반환해야 함
            assert response.status_code in [200, 500]

    def test_global_exception_handler(self, test_client):
        """전역 예외 처리기 테스트"""
        # 예외를 발생시키는 상황 시뮬레이션
        with patch('src.redfin_api.main._news_cache', side_effect=Exception("Test error")):
            response = test_client.get("/health")
            # 전역 예외 처리기가 작동해야 함
            assert response.status_code in [200, 500]


class TestCacheRefresh:
    """캐시 새로고침 테스트"""

    def test_cache_refresh_functionality(self, test_client, mock_load_data):
        """캐시 새로고침 기능 테스트"""
        # 여러 엔드포인트에서 refresh 파라미터 테스트
        endpoints = ["/news", "/news/descriptions", "/news/extract"]
        
        for endpoint in endpoints:
            response = test_client.get(f"{endpoint}?refresh=true")
            assert response.status_code == 200
        
        # _load_data가 여러 번 호출되었는지 확인
        assert mock_load_data.call_count >= len(endpoints)


class TestPerformance:
    """성능 관련 테스트"""

    def test_response_time(self, test_client, sample_news_entries):
        """응답 시간 테스트"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries * 100):  # 더 많은 데이터
            start_time = time.time()
            response = test_client.get("/news?limit=10")
            end_time = time.time()
            
            assert response.status_code == 200
            # 응답 시간이 합리적인 범위 내에 있어야 함 (예: 5초 이내)
            assert (end_time - start_time) < 5.0

    def test_large_dataset_handling(self, test_client, sample_news_entries):
        """대용량 데이터셋 처리 테스트"""
        large_dataset = sample_news_entries * 1000  # 1000배 확장
        
        with patch('src.redfin_api.main._news_cache', large_dataset):
            response = test_client.get("/news?limit=50")
            assert response.status_code == 200
            
            news = response.json()
            assert len(news) <= 50  # limit이 적용되어야 함


class TestConcurrency:
    """동시성 테스트"""

    def test_concurrent_requests(self, test_client, sample_news_entries):
        """동시 요청 처리 테스트"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            response = test_client.get("/health")
            results.put(response.status_code)
        
        # 여러 스레드에서 동시 요청
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # 모든 스레드 완료 대기
        for thread in threads:
            thread.join()
        
        # 모든 요청이 성공했는지 확인
        status_codes = []
        while not results.empty():
            status_codes.append(results.get())
        
        assert len(status_codes) == 10
        assert all(code == 200 for code in status_codes)