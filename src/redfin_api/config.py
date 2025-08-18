from dotenv import load_dotenv ; load_dotenv()
import os
from pathlib import Path
from typing import Optional


# 백엔드 설정
BACKEND = os.getenv("BACKEND", "FILE").upper()

# 파일 백엔드 설정
NEWS_FILE = Path(os.getenv("NEWS_FILE", "ai_news.jsonl"))

# MongoDB 백엔드 설정
MONGO_URI: Optional[str] = os.getenv("MONGO_URI")
MONGO_DB: str = os.getenv("MONGO_DB", "redfin")
MONGO_COL: str = os.getenv("MONGO_COL", "news")

# API 설정
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))
API_RELOAD: bool = os.getenv("API_RELOAD", "false").lower() == "true"

# CORS 설정
CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")
