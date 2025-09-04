"""
RedFin API 설정 관리
"""
from dotenv import load_dotenv
load_dotenv()

import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    """데이터베이스 설정"""
    uri: Optional[str] = None
    database: str = "redfin"
    articles_collection: str = "articles"
    news_collection: str = "news"


class APISettings(BaseModel):
    """API 서버 설정"""
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    debug: bool = False


class CORSSettings(BaseModel):
    """CORS 설정"""
    origins: List[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]


class Settings(BaseSettings):
    """애플리케이션 설정"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"  # 추가 필드 허용
    )

    # 애플리케이션 기본 정보
    app_name: str = "RedFin API"
    app_version: str = "0.2.0"
    app_description: str = "AI RSS News API Service"
    
    # 백엔드 설정
    backend: str = "FILE"
    
    # 파일 백엔드 설정
    news_file: Path = Path("data/all_entries_20250825_025249.jsonl")
    
    # 데이터베이스 설정
    database: DatabaseSettings = DatabaseSettings()
    
    # API 설정
    api: APISettings = APISettings()
    
    # CORS 설정
    cors: CORSSettings = CORSSettings()
    
    # 환경 변수 매핑
    @property
    def mongo_uri(self) -> str:
        """MongoDB 연결 URI"""
        return os.getenv("MONGO_URI") or "mongodb://redfin:Redfin7620%21@localhost:27017/redfin?authSource=admin"
    
    @property
    def mongo_db(self) -> str:
        return os.getenv("MONGO_DB") or self.database.database
    
    @property
    def mongo_articles_col(self) -> str:
        return os.getenv("MONGO_ARTICLES_COL") or self.database.articles_collection
    
    @property
    def mongo_news_col(self) -> str:
        return os.getenv("MONGO_NEWS_COL") or self.database.news_collection
    
    @property
    def api_host(self) -> str:
        return os.getenv("API_HOST") or self.api.host
    
    @property
    def api_port(self) -> int:
        return int(os.getenv("API_PORT", str(self.api.port)))
    
    @property
    def api_reload(self) -> bool:
        return os.getenv("API_RELOAD", str(self.api.reload)).lower() == "true"
    
    @property
    def cors_origins(self) -> List[str]:
        return os.getenv("CORS_ORIGINS", "*").split(",")


# 전역 설정 인스턴스
settings = Settings()

# 하위 호환성을 위한 별칭
BACKEND = settings.backend
NEWS_FILE = settings.news_file
MONGO_URI = settings.mongo_uri
MONGO_DB = settings.mongo_db
MONGO_ARTICLES_COL = settings.mongo_articles_col
MONGO_NEWS_COL = settings.mongo_news_col
API_HOST = settings.api_host
API_PORT = settings.api_port
API_RELOAD = settings.api_reload
CORS_ORIGINS = settings.cors_origins
