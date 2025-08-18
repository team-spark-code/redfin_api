#!/usr/bin/env python3
"""
RedFin API 서버 실행 스크립트
"""

import uvicorn
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.redfin_api.app import app
    from src.redfin_api.config import API_HOST, API_PORT, API_RELOAD
except ImportError as e:
    print(f"Import 오류: {e}")
    print("프로젝트 루트에서 실행하고 있는지 확인하세요.")
    sys.exit(1)

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
            "src.redfin_api.app:app",
            host=API_HOST,
            port=API_PORT,
            reload=API_RELOAD,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 서버가 종료되었습니다.")
    except Exception as e:
        print(f"❌ 서버 실행 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
