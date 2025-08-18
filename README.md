# RedFin API

AI RSS News API Service with FastAPI

## 🚀 기능

- RSS 뉴스 피드 API 서비스
- 파일 및 MongoDB 백엔드 지원
- 실시간 검색 및 필터링
- 신선도 기반 정렬
- RESTful API 인터페이스

## 📋 요구사항

- **Python**: 3.10 이상
- **패키지 관리자**: uv (권장) 또는 pip
- **데이터 백엔드**: 파일 시스템 또는 MongoDB (선택사항)
- **운영체제**: Windows, macOS, Linux

## 🛠️ 환경 설정

### 1. 저장소 클론

```bash
git clone <repository-url>
cd redfin_api
```

### 2. Python 환경 설정

#### uv 사용 (권장)
```bash
# uv 설치 (없는 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 가상환경 생성 및 의존성 설치
uv sync

# 개발 의존성 포함 설치
uv sync --extra dev
```

#### pip 사용
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 개발 모드 설치
pip install -e .
```

### 3. 환경 변수 설정

#### 기본 설정 (파일 백엔드)
```bash
# env.example을 복사하여 .env 파일 생성
cp env.example .env
```

#### 고급 설정 (MongoDB 백엔드)
```bash
# .env 파일 편집
BACKEND=MONGO
MONGO_URI=mongodb://localhost:27017
MONGO_DB=redfin
MONGO_COL=news
```

### 4. 데이터 파일 준비

#### 파일 백엔드 사용 시
```bash
# 샘플 데이터 파일 생성 (없는 경우)
echo '{"source": "Test", "title": "Test News", "link": "https://example.com", "published": "2024-01-01T12:00:00Z", "summary": "Test summary", "authors": ["Test Author"], "tags": ["test"]}' > src/redfin_api/ai_news.jsonl
```

#### MongoDB 백엔드 사용 시
```bash
# MongoDB 설치 및 실행
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS (Homebrew)
brew install mongodb-community
brew services start mongodb-community

# Windows
# MongoDB Community Server 다운로드 및 설치
```

## 🚀 실행 방법

### 방법 1: Makefile 사용 (권장)

```bash
# 도움말 확인
make help

# 서버 실행
make run

# 개발 모드 실행 (자동 재시작)
make run-dev
```

### 방법 2: 실행 스크립트 사용

#### Windows PowerShell
```powershell
# 스크립트 실행 권한 설정 (필요시)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 서버 실행
.\scripts\start.ps1
```

#### Linux/macOS
```bash
# 스크립트 실행 권한 설정
chmod +x scripts/start.sh

# 서버 실행
./scripts/start.sh
```

### 방법 3: 직접 실행

```bash
# Python 스크립트로 실행
python run.py

# uvicorn으로 직접 실행
uvicorn src.redfin_api.main:app --reload --host 0.0.0.0 --port 8000

# 모듈로 실행
python -m src.redfin_api.main
```

### 방법 4: Docker 사용

```bash
# Docker Compose로 실행 (권장)
docker-compose up -d

# MongoDB 포함 실행
docker-compose --profile mongo up -d

# Docker 이미지 직접 빌드 및 실행
make docker-build
make docker-run
```

## 🔧 개발 환경 설정

### 개발 도구 설치

```bash
# 개발 의존성 설치
uv sync --extra dev

# 또는 pip 사용
pip install -e ".[dev]"
```

### 코드 품질 관리

```bash
# 코드 포맷팅
make format

# 린팅 검사
make lint

# 타입 체크
make type-check

# 테스트 실행
make test

# 모든 검사 실행
make check
```

### IDE 설정

#### VS Code
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"]
}
```

#### PyCharm
- Project Structure에서 `src`를 Sources Root로 설정
- Python Interpreter를 가상환경으로 설정

## 📚 API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔌 API 엔드포인트

### 헬스체크
```http
GET /health
```

### 뉴스 소스 목록
```http
GET /sources
```

### 뉴스 목록 조회
```http
GET /news?q=검색어&source=소스명&limit=20&offset=0&sort=fresh&refresh=false
```

#### 쿼리 파라미터:
- `q`: 검색어 (선택사항)
- `source`: 특정 소스 필터 (선택사항)
- `limit`: 조회 개수 (1-100, 기본값: 20)
- `offset`: 오프셋 (기본값: 0)
- `sort`: 정렬 방식 (`fresh` 또는 `time`, 기본값: `fresh`)
- `refresh`: 캐시 새로고침 (기본값: `false`)

## 📊 데이터 형식

### 뉴스 아이템 구조

```json
{
  "source": "뉴스 소스명",
  "title": "뉴스 제목",
  "link": "https://example.com/news/123",
  "published": "2024-01-01T12:00:00Z",
  "summary": "뉴스 요약",
  "authors": ["작성자1", "작성자2"],
  "tags": ["태그1", "태그2"]
}
```

## 🧪 개발

### 개발 워크플로우

```bash
# 1. 개발 의존성 설치
uv sync --extra dev

# 2. 코드 포맷팅
make format

# 3. 린팅 검사
make lint

# 4. 테스트 실행
make test

# 5. 모든 검사 실행
make check
```

### 개별 도구 사용

```bash
# 코드 포맷팅
black src/ tests/
isort src/ tests/

# 린팅
flake8 src/ tests/
mypy src/

# 테스트
pytest tests/ -v
pytest tests/ --cov=src/redfin_api --cov-report=html
```

### 커밋 전 검사

```bash
# 커밋 전 모든 검사 실행
make pre-commit
```

## 📁 프로젝트 구조

```
redfin_api/
├── src/
│   └── redfin_api/
│       ├── __init__.py          # 패키지 초기화
│       ├── app.py               # FastAPI 앱 (기존)
│       ├── main.py              # FastAPI 앱 (새로 생성)
│       ├── models.py            # Pydantic 모델
│       ├── config.py            # 설정 관리
│       └── ai_news.jsonl        # 샘플 뉴스 데이터
├── scripts/
│   ├── start.sh                # Linux/macOS 시작 스크립트
│   └── start.ps1               # Windows 시작 스크립트
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # pytest 설정
│   └── test_api.py             # API 테스트
├── run.py                      # 메인 실행 스크립트
├── pyproject.toml              # 프로젝트 설정 (uv)
├── requirements.txt            # pip 의존성
├── env.example                 # 환경 변수 예제
├── .gitignore                  # Git 무시 파일
├── .dockerignore               # Docker 무시 파일
├── Dockerfile                  # Docker 이미지 설정
├── docker-compose.yml          # Docker Compose 설정
├── Makefile                    # 개발 명령어 모음
└── README.md                   # 프로젝트 문서
```

## 🔧 문제 해결

### 일반적인 문제

#### Import 오류가 발생하는 경우
```bash
# 1. 프로젝트 루트에서 실행하고 있는지 확인
pwd  # redfin_api 디렉토리인지 확인

# 2. 가상환경이 활성화되어 있는지 확인
which python  # venv 경로인지 확인

# 3. 의존성 재설치
uv sync
# 또는
pip install -r requirements.txt
```

#### 뉴스 파일을 찾을 수 없는 경우
```bash
# 1. 환경 변수 확인
echo $NEWS_FILE

# 2. 파일 존재 확인
ls -la src/redfin_api/ai_news.jsonl

# 3. 샘플 데이터 생성
echo '{"source": "Test", "title": "Test News", "link": "https://example.com", "published": "2024-01-01T12:00:00Z", "summary": "Test summary", "authors": ["Test Author"], "tags": ["test"]}' > src/redfin_api/ai_news.jsonl
```

#### MongoDB 연결 오류
```bash
# 1. MongoDB 서비스 상태 확인
# Ubuntu/Debian
sudo systemctl status mongodb

# macOS
brew services list | grep mongodb

# 2. MongoDB 연결 테스트
mongosh mongodb://localhost:27017
```

#### Docker 관련 문제
```bash
# 1. Docker 서비스 상태 확인
docker --version
docker-compose --version

# 2. 컨테이너 로그 확인
docker-compose logs redfin-api

# 3. 컨테이너 재시작
docker-compose restart redfin-api
```

### 디버깅

#### 로그 레벨 설정
```bash
# .env 파일에 추가
LOG_LEVEL=DEBUG
```

#### API 헬스체크
```bash
# 서버 상태 확인
curl http://localhost:8000/health

# 상세 정보 확인
curl http://localhost:8000/docs
```

#### 테스트 실행
```bash
# 단위 테스트
pytest tests/ -v

# 특정 테스트만 실행
pytest tests/test_api.py::test_health_endpoint -v
```

## 🤝 기여

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

MIT License

## 📞 지원

문제가 있거나 질문이 있으시면 이슈를 생성해 주세요.
