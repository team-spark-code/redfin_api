# RedFin API 서버 시작 스크립트 (Windows)

# 오류 발생 시 중단
$ErrorActionPreference = "Stop"

# 스크립트 디렉토리로 이동
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

Set-Location $ProjectDir

# 환경 변수 로드
if (Test-Path ".env") {
    Write-Host "환경 변수 파일 로드 중..."
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Python 가상환경 확인
if (Test-Path "venv") {
    Write-Host "가상환경 활성화 중..."
    & "venv\Scripts\Activate.ps1"
}

# 의존성 확인
Write-Host "의존성 확인 중..."
try {
    python -c "import fastapi, uvicorn" 2>$null
} catch {
    Write-Host "의존성이 설치되지 않았습니다. 설치 중..."
    if (Get-Command "uv" -ErrorAction SilentlyContinue) {
        uv sync
    } else {
        pip install -e .
    }
}

# 서버 시작
Write-Host "RedFin API 서버 시작 중..."
Write-Host "호스트: $env:API_HOST (기본값: 0.0.0.0)"
Write-Host "포트: $env:API_PORT (기본값: 8000)"
Write-Host "백엔드: $env:BACKEND (기본값: FILE)"

# run.py 스크립트 실행
python run.py
