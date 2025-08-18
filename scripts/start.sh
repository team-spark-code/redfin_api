#!/bin/bash

# RedFin API 서버 시작 스크립트

set -euo pipefail

# 스크립트 디렉토리로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# 환경 변수 로드
if [[ -f ".env" ]]; then
    echo "환경 변수 파일 로드 중..."
    export $(grep -v '^#' .env | xargs)
fi

# Python 가상환경 확인
if [[ -d "venv" ]]; then
    echo "가상환경 활성화 중..."
    source venv/bin/activate
fi

# 의존성 확인
echo "의존성 확인 중..."
python -c "import fastapi, uvicorn" 2>/dev/null || {
    echo "의존성이 설치되지 않았습니다. 설치 중..."
    if command -v uv &> /dev/null; then
        uv sync
    else
        pip install -e .
    fi
}

# 서버 시작
echo "RedFin API 서버 시작 중..."
echo "호스트: ${API_HOST:-0.0.0.0}"
echo "포트: ${API_PORT:-8000}"
echo "백엔드: ${BACKEND:-FILE}"

# run.py 스크립트 실행
python run.py
