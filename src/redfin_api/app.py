from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import time
import logging

# 상대 import를 절대 import로 변경
try:
    from .models import NewsOut, HealthResponse, NewsQuery
    from .config import (
        BACKEND, NEWS_FILE, MONGO_URI, MONGO_DB, MONGO_COL,
        API_HOST, API_PORT, API_RELOAD, CORS_ORIGINS
    )
except ImportError:
    # 직접 실행 시 절대 import 사용
    from models import NewsOut, HealthResponse, NewsQuery
    from config import (
        BACKEND, NEWS_FILE, MONGO_URI, MONGO_DB, MONGO_COL,
        API_HOST, API_PORT, API_RELOAD, CORS_ORIGINS
    )

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title="RedFin API",
    description="AI RSS News API Service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _freshness_score(item: Dict[str, Any], now_ts: float) -> float:
    """뉴스 아이템의 신선도 점수 계산"""
    dt_str = item.get("published")
    if not dt_str:
        return 0.0
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        age_h = max(1.0, (now_ts - dt.timestamp()) / 3600.0)
        return 1.0 / age_h
    except Exception as e:
        logger.warning(f"날짜 파싱 오류: {e}")
        return 0.0

# ---- 데이터 백엔드 ----
_news_cache: List[Dict[str, Any]] = []

def _load_file() -> List[Dict[str, Any]]:
    """파일 백엔드에서 데이터 로드"""
    items = []
    
    # 여러 가능한 경로를 시도
    possible_paths = [
        # 1. 현재 스크립트 디렉토리의 ai_news.jsonl
        Path(__file__).parent / "ai_news.jsonl",
        # 2. 설정된 경로
        NEWS_FILE,
        # 3. 상대 경로로 시도
        Path("ai_news.jsonl"),
        # 4. src/redfin_api/ai_news.jsonl
        Path("src/redfin_api/ai_news.jsonl"),
    ]
    
    file_loaded = False
    for file_path in possible_paths:
        if file_path.exists():
            try:
                logger.info(f"뉴스 파일 로드 시도: {file_path}")
                with file_path.open("r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        try:
                            items.append(json.loads(line.strip()))
                        except json.JSONDecodeError as e:
                            logger.warning(f"JSON 파싱 오류 (라인 {line_num}): {e}")
                file_loaded = True
                logger.info(f"뉴스 파일 로드 성공: {file_path} ({len(items)}개 아이템)")
                break
            except Exception as e:
                logger.error(f"파일 읽기 오류 ({file_path}): {e}")
    
    if not file_loaded:
        logger.error(f"뉴스 파일을 찾을 수 없습니다. 시도한 경로들: {[str(p) for p in possible_paths]}")
    
    return items

def _load_mongo() -> List[Dict[str, Any]]:
    """MongoDB 백엔드에서 데이터 로드"""
    if not MONGO_URI:
        logger.error("MongoDB URI가 설정되지 않았습니다")
        return []
    
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI)
        collection = client[MONGO_DB][MONGO_COL]
        items = list(collection.find({}, {"_id": 0}).sort([("published", -1)]))
        client.close()
        logger.info(f"MongoDB에서 {len(items)}개 아이템 로드")
        return items
    except Exception as e:
        logger.error(f"MongoDB 연결 오류: {e}")
        return []

def _load_data() -> List[Dict[str, Any]]:
    """백엔드에 따라 데이터 로드"""
    if BACKEND == "MONGO" and MONGO_URI:
        return _load_mongo()
    return _load_file()

# 초기 데이터 로드
_news_cache = _load_data()
logger.info(f"초기 데이터 로드 완료: {len(_news_cache)}개 아이템")

@app.get("/health", response_model=HealthResponse)
def health():
    """헬스체크 엔드포인트"""
    return HealthResponse(
        ok=True,
        count=len(_news_cache),
        backend=BACKEND,
        version="0.1.0"
    )

@app.get("/sources", response_model=List[str])
def sources():
    """사용 가능한 뉴스 소스 목록"""
    sources_set = {n.get("source") for n in _news_cache if n.get("source")}
    return sorted(sources_set)

@app.get("/news", response_model=List[NewsOut])
def list_news(
    q: Optional[str] = Query(None, description="검색어"),
    source: Optional[str] = Query(None, description="특정 소스 필터"),
    limit: int = Query(20, ge=1, le=100, description="조회 개수"),
    offset: int = Query(0, ge=0, description="오프셋"),
    sort: str = Query("fresh", pattern="^(fresh|time)$", description="정렬 방식"),
    refresh: bool = Query(False, description="캐시 새로고침")
):
    """뉴스 목록 조회"""
    global _news_cache
    
    if refresh:
        logger.info("캐시 새로고침 요청")
        _news_cache = _load_data()

    now_ts = time.time()
    items = _news_cache.copy()

    # 소스 필터링
    if source:
        items = [n for n in items if n.get("source") == source]

    # 검색어 필터링
    if q:
        ql = q.lower()
        def hit(n): 
            return any(ql in (n.get(k) or "").lower() for k in ("title", "summary")) or \
                   ql in " ".join(n.get("tags") or []).lower()
        items = [n for n in items if hit(n)]

    # 정렬
    if sort == "fresh":
        items = sorted(items, key=lambda n: _freshness_score(n, now_ts), reverse=True)
    else:
        items = sorted(items, key=lambda n: n.get("published") or "", reverse=True)

    # 페이지네이션
    result_items = items[offset:offset + limit]
    
    try:
        return [NewsOut(**n) for n in result_items]
    except Exception as e:
        logger.error(f"뉴스 아이템 변환 오류: {e}")
        raise HTTPException(status_code=500, detail="데이터 변환 오류")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 처리"""
    logger.error(f"예상치 못한 오류: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "내부 서버 오류"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD,
        log_level="info"
    )
