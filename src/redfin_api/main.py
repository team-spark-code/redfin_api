from dotenv import load_dotenv ; load_dotenv()
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path
import json
import time
import logging

# 상대 import를 절대 import로 변경
try:
    from .models import NewsOut, HealthResponse, NewsQuery, NewsEntry, NewsDescriptionResponse
    from .config import (
        BACKEND, NEWS_FILE, MONGO_URI, MONGO_DB, MONGO_COL,
        API_HOST, API_PORT, API_RELOAD, CORS_ORIGINS
    )
except ImportError:
    # 직접 실행 시 절대 import 사용
    from models import NewsOut, HealthResponse, NewsQuery, NewsEntry, NewsDescriptionResponse
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
    # published 필드 우선 확인
    dt_str = item.get("published")
    if not dt_str:
        # processed_at 필드 확인
        dt_str = item.get("processed_at")
    
    if not dt_str:
        return 0.0
    
    try:
        # 다양한 날짜 형식 처리
        dt = None
        
        # 1. RFC 2822 형식 (예: "Mon, 25 Aug 2025 06:00:00 GMT")
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(dt_str)
        except:
            pass
        
        # 2. ISO 형식 (예: "2025-08-26T11:47:10.173932")
        if not dt:
            try:
                dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            except:
                pass
        
        # 3. 다른 형식들 시도
        if not dt:
            try:
                dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
            except:
                pass
        
        if dt:
            age_h = max(1.0, (now_ts - dt.timestamp()) / 3600.0)
            return 1.0 / age_h
        else:
            logger.warning(f"지원되지 않는 날짜 형식: {dt_str}")
            return 0.0
            
    except Exception as e:
        logger.warning(f"날짜 파싱 오류: {e}")
        return 0.0

def _normalize_news_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """뉴스 아이템을 표준화된 형태로 변환"""
    normalized = item.copy()
    
    # 두 가지 구조를 통합
    if "guid" in item and "article_text" in item:
        # extract_20250826_105701.json 구조
        normalized["guid"] = item.get("guid")
        normalized["source"] = item.get("source", "")
        normalized["title"] = item.get("title", "")
        normalized["link"] = item.get("link", "")
        normalized["article_text"] = item.get("article_text", "")
        normalized["summary"] = item.get("summary", "")
        normalized["tags"] = item.get("tags", [])
        normalized["content_type"] = item.get("content_type", "NEWS")
        normalized["language"] = item.get("language", "ENGLISH")
        normalized["readability_score"] = item.get("readability_score")
        normalized["key_entities"] = item.get("key_entities", [])
        normalized["processed_at"] = item.get("processed_at")
        normalized["text_length"] = item.get("text_length")
    elif "guid" in item:
        # 기존 상세 구조
        normalized["guid"] = item.get("guid")
        normalized["source"] = item.get("source", "")
        normalized["title"] = item.get("title", "")
        normalized["link"] = item.get("link", "")
        normalized["article_text"] = item.get("article_text", "")
        normalized["summary"] = item.get("summary", "")
        normalized["tags"] = item.get("tags", [])
        normalized["content_type"] = item.get("content_type", "NEWS")
        normalized["language"] = item.get("language", "ENGLISH")
        normalized["readability_score"] = item.get("readability_score")
        normalized["key_entities"] = item.get("key_entities", [])
        normalized["processed_at"] = item.get("processed_at")
        normalized["text_length"] = item.get("text_length")
    elif "type" in item:
        # 간단 구조
        normalized["guid"] = item.get("link")  # link를 ID로 사용
        normalized["source"] = item.get("source", "")
        normalized["title"] = item.get("title", "")
        normalized["link"] = item.get("link", "")
        normalized["article_text"] = item.get("summary", "")  # 간단 구조는 summary를 article_text로 사용
        normalized["summary"] = item.get("summary", "")
        normalized["tags"] = item.get("tags", [])
        normalized["content_type"] = "NEWS"
        normalized["language"] = "ENGLISH"
        normalized["readability_score"] = None
        normalized["key_entities"] = []
        normalized["processed_at"] = item.get("published")
        normalized["text_length"] = len(item.get("summary", ""))
    
    return normalized

# ---- 데이터 백엔드 ----
_news_cache: List[Dict[str, Any]] = []

def _load_file() -> List[Dict[str, Any]]:
    """파일 백엔드에서 데이터 로드"""
    items = []
    
    # 여러 가능한 경로를 시도
    possible_paths = [
        NEWS_FILE,
        Path("data/extract_20250826_105701.json"),
    ]
    print(f"NEWS_FILE: {NEWS_FILE}")

    file_loaded = False
    for file_path in possible_paths:
        if file_path.exists():
            try:
                logger.info(f"뉴스 파일 로드 시도: {file_path}")
                with file_path.open("r", encoding="utf-8") as f:
                    # 파일 확장자에 따라 다른 읽기 방식 사용
                    if file_path.suffix == ".jsonl":
                        # JSONL 파일: 한 줄씩 읽기
                        for line_num, line in enumerate(f, 1):
                            try:
                                if line.strip():  # 빈 줄 무시
                                    items.append(json.loads(line.strip()))
                            except json.JSONDecodeError as e:
                                logger.warning(f"JSONL 파싱 오류 (라인 {line_num}): {e}")
                    else:
                        # JSON 파일: 배열 형태로 읽기
                        try:
                            data = json.load(f)
                            if isinstance(data, list):
                                items = data
                            else:
                                logger.error(f"JSON 파일이 배열 형태가 아닙니다: {file_path}")
                                continue
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON 파싱 오류 ({file_path}): {e}")
                            continue
                        
                file_loaded = True
                logger.info(f"뉴스 파일 로드 성공: {file_path} ({len(items)}개 아이템)")
                break
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 오류 ({file_path}): {e}")
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
        items = list(collection.find({}, {"_id": 0}).sort([("pub_date", -1)]))
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

@app.get("/")
def root():
    """루트 경로 - API 정보 및 사용법"""
    return {
        "message": "RedFin AI News API에 오신 것을 환영합니다!",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "news": "/news",
            "news_descriptions": "/news/descriptions",
            "news_extract": "/news/extract",
            "sources": "/sources",
            "groups": "/groups",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "usage": {
            "뉴스 조회": "GET /news?limit=10",
            "뉴스 설명 조회": "GET /news/descriptions?limit=10",
            "Extract 뉴스 조회": "GET /news/extract?limit=10",
            "소스별 필터링": "GET /news?source=OpenAI Blog",
            "검색": "GET /news?q=AI",
            "정렬": "GET /news?sort=fresh"
        },
        "data_structures": {
            "standard": "기본 뉴스 구조 (NewsOut, NewsEntry)",
            "extract": "extract_20250826_105701.json 구조 (NewsEntry)"
        }
    }

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

@app.get("/groups", response_model=List[str])
def groups():
    """사용 가능한 뉴스 그룹 목록"""
    groups_set = {n.get("group") for n in _news_cache if n.get("group")}
    return sorted(groups_set)

@app.get("/news/descriptions", response_model=NewsDescriptionResponse)
def list_news_descriptions(
    q: Optional[str] = Query(None, description="검색어"),
    source: Optional[str] = Query(None, description="특정 소스 필터"),
    group: Optional[str] = Query(None, description="특정 그룹 필터"),
    limit: int = Query(20, ge=1, le=100, description="조회 개수"),
    offset: int = Query(0, ge=0, description="오프셋"),
    sort: str = Query("fresh", pattern="^(fresh|time)$", description="정렬 방식"),
    refresh: bool = Query(False, description="캐시 새로고침")
):
    """뉴스 description 목록 조회"""
    global _news_cache
    
    if refresh:
        logger.info("캐시 새로고침 요청")
        _news_cache = _load_data()

    now_ts = time.time()
    items = [_normalize_news_item(item) for item in _news_cache]

    # 소스 필터링
    if source:
        items = [n for n in items if n.get("source") == source]

    # 그룹 필터링
    if group:
        items = [n for n in items if n.get("group") == group]

    # 검색어 필터링
    if q:
        ql = q.lower()
        def hit(n): 
            return any(ql in (n.get(k) or "").lower() for k in ("title", "summary", "article_text")) or \
                   ql in " ".join(n.get("tags") or []).lower()
        items = [n for n in items if hit(n)]

    # 정렬
    if sort == "fresh":
        items = sorted(items, key=lambda n: _freshness_score(n, now_ts), reverse=True)
    else:
        items = sorted(items, key=lambda n: n.get("processed_at") or "", reverse=True)

    # 페이지네이션
    result_items = items[offset:offset + limit]
    
    try:
        # NewsEntry 모델로 변환
        news_entries = []
        for item in result_items:
            try:
                # extract_20250826_105701.json 구조에 맞는 필드 설정
                news_data = {
                    "guid": item.get("guid", ""),
                    "source": item.get("source", ""),
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "article_text": item.get("article_text", ""),
                    "summary": item.get("summary", ""),
                    "tags": item.get("tags", []),
                    "content_type": item.get("content_type", "NEWS"),
                    "language": item.get("language", "ENGLISH"),
                    "readability_score": item.get("readability_score"),
                    "key_entities": item.get("key_entities", []),
                    "processed_at": item.get("processed_at"),
                    "text_length": item.get("text_length")
                }
                news_entry = NewsEntry(**news_data)
                news_entries.append(news_entry)
            except Exception as e:
                logger.warning(f"뉴스 엔트리 변환 오류 (guid: {item.get('guid', 'unknown')}): {e}")
                continue
        
        return NewsDescriptionResponse(
            success=True,
            count=len(news_entries),
            data=news_entries,
            total=len(items)
        )
    except Exception as e:
        logger.error(f"뉴스 description 응답 생성 오류: {e}")
        raise HTTPException(status_code=500, detail="데이터 변환 오류")

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
    items = [_normalize_news_item(item) for item in _news_cache]

    # 소스 필터링
    if source:
        items = [n for n in items if n.get("source") == source]

    # 검색어 필터링
    if q:
        ql = q.lower()
        def hit(n): 
            return any(ql in (n.get(k) or "").lower() for k in ("title", "summary", "article_text")) or \
                   ql in " ".join(n.get("tags") or []).lower()
        items = [n for n in items if hit(n)]

    # 정렬
    if sort == "fresh":
        items = sorted(items, key=lambda n: _freshness_score(n, now_ts), reverse=True)
    else:
        items = sorted(items, key=lambda n: n.get("processed_at") or "", reverse=True)

    # 페이지네이션
    result_items = items[offset:offset + limit]
    
    try:
        # NewsOut 모델로 변환
        news_outputs = []
        for item in result_items:
            try:
                news_data = {
                    "source": item.get("source", ""),
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "summary": item.get("summary", ""),
                    "published": item.get("processed_at") or item.get("published", ""),
                    "tags": item.get("tags", [])
                }
                news_output = NewsOut(**news_data)
                news_outputs.append(news_output)
            except Exception as e:
                logger.warning(f"뉴스 출력 변환 오류 (guid: {item.get('guid', 'unknown')}): {e}")
                continue
        
        return news_outputs
    except Exception as e:
        logger.error(f"뉴스 아이템 변환 오류: {e}")
        raise HTTPException(status_code=500, detail="데이터 변환 오류")

@app.get("/news/extract", response_model=List[NewsEntry])
def list_extract_news(
    q: Optional[str] = Query(None, description="검색어"),
    source: Optional[str] = Query(None, description="특정 소스 필터"),
    limit: int = Query(20, ge=1, le=100, description="조회 개수"),
    offset: int = Query(0, ge=0, description="오프셋"),
    sort: str = Query("fresh", pattern="^(fresh|time)$", description="정렬 방식"),
    refresh: bool = Query(False, description="캐시 새로고침")
):
    """extract_20250826_105701.json 구조의 뉴스 목록 조회"""
    global _news_cache
    
    if refresh:
        logger.info("캐시 새로고침 요청")
        _news_cache = _load_data()

    now_ts = time.time()
    items = _news_cache.copy()  # 원본 데이터 사용

    # 소스 필터링
    if source:
        items = [n for n in items if n.get("source") == source]

    # 검색어 필터링
    if q:
        ql = q.lower()
        def hit(n): 
            return any(ql in (n.get(k) or "").lower() for k in ("title", "summary", "article_text")) or \
                   ql in " ".join(n.get("tags") or []).lower()
        items = [n for n in items if hit(n)]

    # 정렬
    if sort == "fresh":
        items = sorted(items, key=lambda n: _freshness_score(n, now_ts), reverse=True)
    else:
        items = sorted(items, key=lambda n: n.get("processed_at") or n.get("published") or "", reverse=True)

    # 페이지네이션
    result_items = items[offset:offset + limit]
    
    try:
        # NewsEntry 모델로 변환
        extract_news_entries = []
        for item in result_items:
            try:
                # extract_20250826_105701.json 구조에 맞는 필드만 추출
                extract_data = {
                    "guid": item.get("guid", ""),
                    "source": item.get("source", ""),
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "article_text": item.get("article_text", ""),
                    "summary": item.get("summary", ""),
                    "tags": item.get("tags", []),
                    "content_type": item.get("content_type", "NEWS"),
                    "language": item.get("language", "ENGLISH"),
                    "readability_score": item.get("readability_score"),
                    "key_entities": item.get("key_entities", []),
                    "processed_at": item.get("processed_at"),
                    "text_length": item.get("text_length")
                }
                extract_entry = NewsEntry(**extract_data)
                extract_news_entries.append(extract_entry)
            except Exception as e:
                logger.warning(f"Extract 뉴스 엔트리 변환 오류 (guid: {item.get('guid', 'unknown')}): {e}")
                continue
        
        return extract_news_entries
    except Exception as e:
        logger.error(f"Extract 뉴스 아이템 변환 오류: {e}")
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
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD,
        log_level="info"
    )
