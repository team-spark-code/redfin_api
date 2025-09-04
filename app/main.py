"""
RedFin API - FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.database import database
from .api.news import router as news_router
from .api.articles import router as articles_router

# FastAPI 앱 초기화
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
)

# API 라우터 등록
app.include_router(news_router, prefix="/api/v1")
app.include_router(articles_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    await database.connect()


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    await database.disconnect()


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "RedFin API 서비스",
        "version": settings.app_version,
        "docs": "/docs",
        "endpoints": {
            "news": "/api/v1/news",
            "articles": "/api/v1/articles",
            "health": "/api/v1/news/health"
        }
    }


@app.get("/health")
async def health_check():
    """기본 헬스체크"""
    return {"status": "healthy", "version": settings.app_version}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 처리"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "내부 서버 오류가 발생했습니다",
            "error": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level="info"
    )
