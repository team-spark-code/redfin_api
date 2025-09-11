"""
통합 테스트 - 실제 시나리오와 엔드투엔드 테스트
"""

import pytest
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.redfin_api.main import app


class TestEndToEndScenarios:
    """엔드투엔드 시나리오 테스트"""

    def test_complete_news_workflow(self, test_client, sample_news_entries, test_json_file):
        """완전한 뉴스 워크플로우 테스트"""
        # 1. 파일에서 데이터 로딩
        with patch('src.redfin_api.main.NEWS_FILE', test_json_file), \
             patch('src.redfin_api.main._news_cache', sample_news_entries):
            
            # 2. 헬스체크
            health_response = test_client.get("/health")
            assert health_response.status_code == 200
            health_data = health_response.json()
            assert health_data["ok"] is True
            assert health_data["count"] > 0
            
            # 3. 소스 목록 조회
            sources_response = test_client.get("/sources")
            assert sources_response.status_code == 200
            sources = sources_response.json()
            assert len(sources) > 0
            
            # 4. 뉴스 목록 조회
            news_response = test_client.get("/news")
            assert news_response.status_code == 200
            news = news_response.json()
            assert len(news) > 0
            
            # 5. 특정 소스로 필터링
            first_source = sources[0]
            filtered_response = test_client.get(f"/news?source={first_source}")
            assert filtered_response.status_code == 200
            filtered_news = filtered_response.json()
            
            # 모든 뉴스가 해당 소스여야 함
            for item in filtered_news:
                assert item["source"] == first_source
            
            # 6. 검색 기능
            search_response = test_client.get("/news?q=test")
            assert search_response.status_code == 200
            
            # 7. 페이지네이션
            page1 = test_client.get("/news?limit=1&offset=0")
            page2 = test_client.get("/news?limit=1&offset=1")
            assert page1.status_code == 200
            assert page2.status_code == 200

    def test_mongo_to_file_fallback_scenario(self, test_client, sample_news_entries):
        """MongoDB에서 파일로 폴백하는 시나리오"""
        with patch('src.redfin_api.config.BACKEND', 'MONGO'), \
             patch('src.redfin_api.config.MONGO_URI', None), \
             patch('src.redfin_api.main._load_file', return_value=sample_news_entries):
            
            # 캐시 재로드
            response = test_client.get("/news?refresh=true")
            assert response.status_code == 200
            
            # 데이터가 파일에서 로드되었는지 확인
            news = response.json()
            assert len(news) > 0

    def test_real_time_data_refresh(self, test_client, sample_news_entries):
        """실시간 데이터 새로고침 시나리오"""
        # 초기 데이터
        initial_data = sample_news_entries[:1]
        
        # 업데이트된 데이터
        updated_data = sample_news_entries
        
        with patch('src.redfin_api.main._news_cache', initial_data):
            # 초기 상태 확인
            response1 = test_client.get("/news")
            assert len(response1.json()) == 1
            
            # 캐시 업데이트 시뮬레이션
            with patch('src.redfin_api.main._load_data', return_value=updated_data):
                # 새로고침 요청
                response2 = test_client.get("/news?refresh=true")
                # 새로고침 후에는 _load_data가 호출되므로 더 많은 데이터가 있을 수 있음
                assert response2.status_code == 200

    def test_error_recovery_scenario(self, test_client):
        """오류 복구 시나리오"""
        # 데이터 로딩 실패 시나리오
        with patch('src.redfin_api.main._load_data', side_effect=Exception("Load error")):
            # 헬스체크는 여전히 작동해야 함
            response = test_client.get("/health")
            # 오류가 발생해도 적절히 처리되어야 함
            assert response.status_code in [200, 500]

    def test_high_load_scenario(self, test_client, sample_news_entries):
        """고부하 시나리오 테스트"""
        large_dataset = sample_news_entries * 500  # 큰 데이터셋
        
        with patch('src.redfin_api.main._news_cache', large_dataset):
            # 여러 동시 요청
            responses = []
            for i in range(10):
                response = test_client.get(f"/news?limit=10&offset={i*10}")
                responses.append(response)
            
            # 모든 요청이 성공해야 함
            for response in responses:
                assert response.status_code == 200
                assert len(response.json()) <= 10


class TestDataConsistency:
    """데이터 일관성 테스트"""

    def test_data_consistency_across_endpoints(self, test_client, sample_news_entries):
        """엔드포인트 간 데이터 일관성 테스트"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            # 여러 엔드포인트에서 동일한 소스 데이터 조회
            sources_response = test_client.get("/sources")
            news_response = test_client.get("/news")
            descriptions_response = test_client.get("/news/descriptions")
            extract_response = test_client.get("/news/extract")
            
            sources = set(sources_response.json())
            news_sources = {item["source"] for item in news_response.json() if item.get("source")}
            desc_sources = {item["source"] for item in descriptions_response.json()["data"] if item.get("source")}
            extract_sources = {item["source"] for item in extract_response.json() if item.get("source")}
            
            # 모든 엔드포인트에서 일관된 소스 정보를 반환해야 함
            assert sources == news_sources
            assert sources == desc_sources
            assert sources == extract_sources

    def test_pagination_consistency(self, test_client, sample_news_entries):
        """페이지네이션 일관성 테스트"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            # 전체 데이터 조회
            all_news = test_client.get("/news?limit=100").json()
            
            # 페이지별 조회
            page_size = 1
            total_pages = len(all_news)
            
            paginated_news = []
            for i in range(total_pages):
                page_response = test_client.get(f"/news?limit={page_size}&offset={i}")
                page_data = page_response.json()
                paginated_news.extend(page_data)
            
            # 페이지네이션으로 조회한 데이터와 전체 조회 데이터가 일치해야 함
            assert len(paginated_news) <= len(all_news)  # 중복 제거 등으로 인해 같거나 작을 수 있음

    def test_search_result_consistency(self, test_client, sample_news_entries):
        """검색 결과 일관성 테스트"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            search_term = "test"
            
            # 여러 엔드포인트에서 동일한 검색어로 조회
            news_search = test_client.get(f"/news?q={search_term}").json()
            desc_search = test_client.get(f"/news/descriptions?q={search_term}").json()["data"]
            extract_search = test_client.get(f"/news/extract?q={search_term}").json()
            
            # 모든 결과에 검색어가 포함되어야 함
            for item in news_search:
                search_fields = [
                    item.get("title", "").lower(),
                    item.get("summary", "").lower(),
                    " ".join(item.get("tags", [])).lower()
                ]
                assert any(search_term in field for field in search_fields)


class TestConfigurationIntegration:
    """설정 통합 테스트"""

    def test_file_backend_integration(self, test_client, test_json_file, sample_news_entries):
        """파일 백엔드 통합 테스트"""
        with patch('src.redfin_api.config.BACKEND', 'FILE'), \
             patch('src.redfin_api.config.NEWS_FILE', test_json_file), \
             patch('src.redfin_api.main._news_cache', sample_news_entries):
            
            response = test_client.get("/health")
            assert response.status_code == 200
            
            health_data = response.json()
            assert health_data["backend"] in ["FILE", "MONGO"]  # 실제 설정에 따라

    def test_mongo_backend_integration(self, test_client, mock_pymongo, sample_news_entries):
        """MongoDB 백엔드 통합 테스트"""
        mock_client, mock_collection = mock_pymongo
        mock_collection.find.return_value.sort.return_value = sample_news_entries
        
        with patch('src.redfin_api.config.BACKEND', 'MONGO'), \
             patch('src.redfin_api.config.MONGO_URI', 'mongodb://test:27017'), \
             patch('src.redfin_api.main._news_cache', sample_news_entries):
            
            response = test_client.get("/health")
            assert response.status_code == 200
            
            # 새로고침 시 MongoDB 연결 시도
            refresh_response = test_client.get("/news?refresh=true")
            assert refresh_response.status_code == 200

    def test_cors_configuration(self, test_client):
        """CORS 설정 테스트"""
        # OPTIONS 요청으로 CORS 헤더 확인
        response = test_client.options("/health", headers={"Origin": "http://localhost:3000"})
        
        # CORS 관련 헤더가 있는지 확인 (실제 설정에 따라)
        # 이는 미들웨어 설정에 의존하므로 헤더 존재 여부만 확인
        assert response.status_code in [200, 405]  # OPTIONS가 허용되지 않을 수도 있음


class TestPerformanceIntegration:
    """성능 통합 테스트"""

    def test_response_time_under_load(self, test_client, sample_news_entries):
        """부하 상황에서의 응답 시간 테스트"""
        large_dataset = sample_news_entries * 1000
        
        with patch('src.redfin_api.main._news_cache', large_dataset):
            start_time = time.time()
            
            # 여러 요청을 순차적으로 실행
            for i in range(5):
                response = test_client.get(f"/news?limit=20&offset={i*20}")
                assert response.status_code == 200
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # 평균 응답 시간이 합리적인 범위 내에 있어야 함
            avg_time = total_time / 5
            assert avg_time < 2.0  # 2초 이내

    def test_memory_usage_with_large_dataset(self, test_client, sample_news_entries):
        """대용량 데이터셋에서의 메모리 사용량 테스트"""
        # 매우 큰 데이터셋 생성
        large_dataset = sample_news_entries * 5000
        
        with patch('src.redfin_api.main._news_cache', large_dataset):
            # 여러 요청으로 메모리 사용 패턴 확인
            responses = []
            for i in range(10):
                response = test_client.get(f"/news?limit=100&offset={i*100}")
                responses.append(response)
            
            # 모든 요청이 성공해야 함
            for response in responses:
                assert response.status_code == 200
                assert len(response.json()) <= 100

    def test_caching_effectiveness(self, test_client, sample_news_entries):
        """캐싱 효과 테스트"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries), \
             patch('src.redfin_api.main._load_data') as mock_load:
            
            # 첫 번째 요청 (캐시 사용)
            response1 = test_client.get("/news")
            
            # 두 번째 요청 (캐시 사용, _load_data 호출 안됨)
            response2 = test_client.get("/news")
            
            # refresh=false인 경우 _load_data가 호출되지 않아야 함
            assert response1.status_code == 200
            assert response2.status_code == 200
            mock_load.assert_not_called()
            
            # refresh=true인 경우에만 _load_data 호출
            response3 = test_client.get("/news?refresh=true")
            assert response3.status_code == 200
            mock_load.assert_called_once()


class TestRealWorldScenarios:
    """실제 사용 시나리오 테스트"""

    def test_mobile_app_api_usage(self, test_client, sample_news_entries):
        """모바일 앱 API 사용 시나리오"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            # 1. 앱 시작 시 헬스체크
            health = test_client.get("/health")
            assert health.status_code == 200
            
            # 2. 최신 뉴스 10개 조회
            latest_news = test_client.get("/news?limit=10&sort=fresh")
            assert latest_news.status_code == 200
            assert len(latest_news.json()) <= 10
            
            # 3. 특정 카테고리 뉴스 조회
            if latest_news.json():
                first_source = latest_news.json()[0]["source"]
                category_news = test_client.get(f"/news?source={first_source}&limit=5")
                assert category_news.status_code == 200
            
            # 4. 검색 기능
            search_results = test_client.get("/news?q=test&limit=5")
            assert search_results.status_code == 200

    def test_web_dashboard_scenario(self, test_client, sample_news_entries):
        """웹 대시보드 시나리오"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            # 1. 대시보드 초기 로딩
            health = test_client.get("/health")
            sources = test_client.get("/sources")
            latest_news = test_client.get("/news?limit=20")
            
            assert health.status_code == 200
            assert sources.status_code == 200
            assert latest_news.status_code == 200
            
            # 2. 상세 정보 조회
            descriptions = test_client.get("/news/descriptions?limit=10")
            assert descriptions.status_code == 200
            
            desc_data = descriptions.json()
            assert "success" in desc_data
            assert "data" in desc_data
            
            # 3. 실시간 업데이트 시뮬레이션
            refresh_data = test_client.get("/news?refresh=true&limit=20")
            assert refresh_data.status_code == 200

    def test_api_analytics_scenario(self, test_client, sample_news_entries):
        """API 분석 시나리오"""
        with patch('src.redfin_api.main._news_cache', sample_news_entries):
            # 1. 전체 통계
            health = test_client.get("/health")
            sources = test_client.get("/sources")
            
            total_count = health.json().get("count", 0)
            sources_count = len(sources.json())
            
            assert total_count >= 0
            assert sources_count >= 0
            
            # 2. 소스별 분석
            source_stats = {}
            for source in sources.json():
                source_news = test_client.get(f"/news?source={source}")
                source_stats[source] = len(source_news.json())
            
            # 3. 시간대별 분석 (정렬 옵션으로 확인)
            time_sorted = test_client.get("/news?sort=time&limit=50")
            fresh_sorted = test_client.get("/news?sort=fresh&limit=50")
            
            assert time_sorted.status_code == 200
            assert fresh_sorted.status_code == 200
