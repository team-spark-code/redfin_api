#!/usr/bin/env python3
"""
RedFin API 서버 실행 스크립트
"""

import uvicorn
from app.core.config import API_HOST, API_PORT, API_RELOAD

def main():
    """메인 실행 함수"""
    print("🚀 RedFin API 서버 시작 중...")
    print(f"📍 호스트: {API_HOST}")
    print(f"🔌 포트: {API_PORT}")
    print(f"🔄 자동 재시작: {API_RELOAD}")
    print("📚 API 문서: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "app.main:app",
            host=API_HOST,
            port=API_PORT,
            reload=API_RELOAD,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 서버가 종료되었습니다.")
    except Exception as e:
        print(f"❌ 서버 실행 오류: {e}")
        exit(1)

if __name__ == "__main__":
    main()
