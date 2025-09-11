"""
설정(config) 모듈 단위 테스트
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from src.redfin_api import config


class TestConfigDefaults:
    """기본 설정 테스트"""

    def test_default_backend(self):
        """기본 백엔드 설정 테스트"""
        with patch.dict(os.environ, {}, clear=True):
            # 환경변수를 모두 제거하고 모듈 재로드
            import importlib
            importlib.reload(config)
            assert config.BACKEND == "FILE"

    def test_default_api_settings(self):
        """기본 API 설정 테스트"""
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            importlib.reload(config)
            assert config.API_HOST == "0.0.0.0"
            assert config.API_PORT == 8000
            assert config.API_RELOAD is False

    def test_default_cors_origins(self):
        """기본 CORS 설정 테스트"""
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            importlib.reload(config)
            assert config.CORS_ORIGINS == ["*"]

    def test_default_mongo_settings(self):
        """기본 MongoDB 설정 테스트"""
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            importlib.reload(config)
            assert config.MONGO_URI is None
            assert config.MONGO_DB == "redfin"
            assert config.MONGO_COL == "news"


class TestConfigEnvironmentVariables:
    """환경변수 기반 설정 테스트"""

    def test_backend_from_env(self):
        """환경변수에서 백엔드 설정 읽기"""
        with patch.dict(os.environ, {"BACKEND": "mongo"}):
            import importlib
            importlib.reload(config)
            assert config.BACKEND == "MONGO"  # 대문자로 변환됨

    def test_api_settings_from_env(self):
        """환경변수에서 API 설정 읽기"""
        with patch.dict(os.environ, {
            "API_HOST": "127.0.0.1",
            "API_PORT": "9000",
            "API_RELOAD": "true"
        }):
            import importlib
            importlib.reload(config)
            assert config.API_HOST == "127.0.0.1"
            assert config.API_PORT == 9000
            assert config.API_RELOAD is True

    def test_mongo_settings_from_env(self):
        """환경변수에서 MongoDB 설정 읽기"""
        with patch.dict(os.environ, {
            "MONGO_URI": "mongodb://test:27017",
            "MONGO_DB": "test_db",
            "MONGO_COL": "test_collection"
        }):
            import importlib
            importlib.reload(config)
            assert config.MONGO_URI == "mongodb://test:27017"
            assert config.MONGO_DB == "test_db"
            assert config.MONGO_COL == "test_collection"

    def test_cors_origins_from_env(self):
        """환경변수에서 CORS origins 읽기"""
        with patch.dict(os.environ, {
            "CORS_ORIGINS": "http://localhost:3000,https://example.com"
        }):
            import importlib
            importlib.reload(config)
            expected = ["http://localhost:3000", "https://example.com"]
            assert config.CORS_ORIGINS == expected

    def test_news_file_from_env(self):
        """환경변수에서 뉴스 파일 경로 읽기"""
        with patch.dict(os.environ, {"NEWS_FILE": "/custom/path/news.json"}):
            import importlib
            importlib.reload(config)
            assert str(config.NEWS_FILE) == "/custom/path/news.json"


class TestConfigTypes:
    """설정 타입 변환 테스트"""

    def test_api_port_type_conversion(self):
        """API_PORT 정수 변환 테스트"""
        with patch.dict(os.environ, {"API_PORT": "8080"}):
            import importlib
            importlib.reload(config)
            assert isinstance(config.API_PORT, int)
            assert config.API_PORT == 8080

    def test_api_reload_boolean_conversion(self):
        """API_RELOAD 불린 변환 테스트"""
        # True 케이스들
        for true_value in ["true", "True", "TRUE", "1", "yes"]:
            with patch.dict(os.environ, {"API_RELOAD": true_value}):
                import importlib
                importlib.reload(config)
                assert config.API_RELOAD is True, f"Failed for value: {true_value}"

        # False 케이스들
        for false_value in ["false", "False", "FALSE", "0", "no", ""]:
            with patch.dict(os.environ, {"API_RELOAD": false_value}):
                import importlib
                importlib.reload(config)
                assert config.API_RELOAD is False, f"Failed for value: {false_value}"

    def test_news_file_path_type(self):
        """NEWS_FILE Path 타입 테스트"""
        import importlib
        importlib.reload(config)
        assert isinstance(config.NEWS_FILE, Path)

    def test_cors_origins_list_type(self):
        """CORS_ORIGINS 리스트 타입 테스트"""
        import importlib
        importlib.reload(config)
        assert isinstance(config.CORS_ORIGINS, list)


class TestConfigValidation:
    """설정 유효성 검증 테스트"""

    def test_invalid_api_port(self):
        """잘못된 API_PORT 처리"""
        with patch.dict(os.environ, {"API_PORT": "invalid"}):
            with pytest.raises(ValueError):
                import importlib
                importlib.reload(config)

    def test_empty_cors_origins(self):
        """빈 CORS_ORIGINS 처리"""
        with patch.dict(os.environ, {"CORS_ORIGINS": ""}):
            import importlib
            importlib.reload(config)
            assert config.CORS_ORIGINS == [""]

    def test_backend_case_insensitive(self):
        """백엔드 설정 대소문자 무관 테스트"""
        for backend_value in ["file", "FILE", "File", "mongo", "MONGO", "Mongo"]:
            with patch.dict(os.environ, {"BACKEND": backend_value}):
                import importlib
                importlib.reload(config)
                assert config.BACKEND in ["FILE", "MONGO"]


class TestConfigIntegration:
    """설정 통합 테스트"""

    def test_file_backend_configuration(self):
        """파일 백엔드 완전 설정 테스트"""
        with patch.dict(os.environ, {
            "BACKEND": "FILE",
            "NEWS_FILE": "/path/to/news.json",
            "API_HOST": "localhost",
            "API_PORT": "8000"
        }):
            import importlib
            importlib.reload(config)
            assert config.BACKEND == "FILE"
            assert str(config.NEWS_FILE) == "/path/to/news.json"
            assert config.API_HOST == "localhost"
            assert config.API_PORT == 8000

    def test_mongo_backend_configuration(self):
        """MongoDB 백엔드 완전 설정 테스트"""
        with patch.dict(os.environ, {
            "BACKEND": "MONGO",
            "MONGO_URI": "mongodb://localhost:27017",
            "MONGO_DB": "production_db",
            "MONGO_COL": "articles",
            "API_HOST": "0.0.0.0",
            "API_PORT": "9000"
        }):
            import importlib
            importlib.reload(config)
            assert config.BACKEND == "MONGO"
            assert config.MONGO_URI == "mongodb://localhost:27017"
            assert config.MONGO_DB == "production_db"
            assert config.MONGO_COL == "articles"
            assert config.API_HOST == "0.0.0.0"
            assert config.API_PORT == 9000

    def test_development_configuration(self):
        """개발 환경 설정 테스트"""
        with patch.dict(os.environ, {
            "BACKEND": "FILE",
            "NEWS_FILE": "data/test_news.json",
            "API_HOST": "127.0.0.1",
            "API_PORT": "8000",
            "API_RELOAD": "true",
            "CORS_ORIGINS": "http://localhost:3000,http://localhost:8080"
        }):
            import importlib
            importlib.reload(config)
            assert config.BACKEND == "FILE"
            assert config.API_HOST == "127.0.0.1"
            assert config.API_RELOAD is True
            assert len(config.CORS_ORIGINS) == 2
            assert "http://localhost:3000" in config.CORS_ORIGINS

    def test_production_configuration(self):
        """프로덕션 환경 설정 테스트"""
        with patch.dict(os.environ, {
            "BACKEND": "MONGO",
            "MONGO_URI": "mongodb://prod-cluster:27017",
            "MONGO_DB": "redfin_prod",
            "API_HOST": "0.0.0.0",
            "API_PORT": "80",
            "API_RELOAD": "false",
            "CORS_ORIGINS": "https://redfin.com,https://api.redfin.com"
        }):
            import importlib
            importlib.reload(config)
            assert config.BACKEND == "MONGO"
            assert config.MONGO_URI == "mongodb://prod-cluster:27017"
            assert config.MONGO_DB == "redfin_prod"
            assert config.API_HOST == "0.0.0.0"
            assert config.API_PORT == 80
            assert config.API_RELOAD is False
            assert "https://redfin.com" in config.CORS_ORIGINS
