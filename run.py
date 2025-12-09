#!/usr/bin/env python3
"""
RedFin API 서버 실행 스크립트
"""
import uvicorn
from app.core.config import settings


def main():
    """메인 실행 함수"""
    print("🚀 RedFin API 서버 시작 중...")
    print(f"📍 호스트: {settings.api_host}")
    print(f"🔌 포트: {settings.api_port}")
    print(f"🔄 자동 재시작: {settings.api_reload}")
    print(f"📚 API 문서: http://{settings.api_host}:{settings.api_port}/docs")
    print(f"📖 ReDoc: http://{settings.api_host}:{settings.api_port}/redoc")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "app.main:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.api_reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 서버가 종료되었습니다.")
    except Exception as e:
        print(f"❌ 서버 실행 오류: {e}")
        exit(1)


if __name__ == "__main__":
    main()
