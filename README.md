# RedFin API

AI RSS News API Service with FastAPI

## 🚀 기능

- RSS 뉴스 피드 API 서비스
- 파일 및 MongoDB 백엔드 지원
- 실시간 검색 및 필터링
- 신선도 기반 정렬
- RESTful API 인터페이스

## 📋 요구사항

- Python 3.10+
- FastAPI
- Uvicorn

## 🛠️ 설치

### 1. 의존성 설치

```bash
# uv 사용 (권장)
uv sync

# 또는 pip 사용
pip install -e .
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 설정을 추가하세요:

```bash
# 백엔드 설정 (FILE 또는 MONGO)
BACKEND=FILE

# 파일 백엔드 설정
NEWS_FILE=/path/to/your/news.jsonl

# MongoDB 백엔드 설정 (선택사항)
MONGO_URI=mongodb://localhost:27017
MONGO_DB=redfin
MONGO_COL=news

# API 설정
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

# CORS 설정
CORS_ORIGINS=*
```

## 🚀 실행

### 방법 1: 실행 스크립트 사용 (권장)

#### Windows
```powershell
.\scripts\start.ps1
```

#### Linux/Mac
```bash
chmod +x scripts/start.sh
./scripts/start.sh
```

### 방법 2: 직접 실행

```bash
# 프로젝트 루트에서
python run.py

# 또는 uvicorn 사용
uvicorn redfin_api.main:app --reload --host 0.0.0.0 --port 8000
```

### 방법 3: 모듈로 실행

```bash
# 프로젝트 루트에서
python -m redfin_api.main
```

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

### 개발 의존성 설치

```bash
uv sync --extra dev
```

### 코드 포맷팅

```bash
# Black으로 코드 포맷팅
black src/

# isort로 import 정렬
isort src/
```

### 타입 체크

```bash
mypy src/
```

### 테스트 실행

```bash
pytest
```

## 📁 프로젝트 구조

```
redfin_api/
├── src/
│   └── redfin_api/
│       ├── __init__.py
│       ├── main.py          # FastAPI 앱 및 엔드포인트
│       ├── models.py        # Pydantic 모델
│       └── config.py        # 설정 관리
├── scripts/
│   ├── start.sh            # Linux/Mac 시작 스크립트
│   └── start.ps1           # Windows 시작 스크립트
├── tests/                   # 테스트 파일
├── run.py                  # 메인 실행 스크립트
├── pyproject.toml          # 프로젝트 설정
├── env.example             # 환경 변수 예제
└── README.md               # 프로젝트 문서
```

## 🔧 문제 해결

### Import 오류가 발생하는 경우

1. 프로젝트 루트에서 실행하고 있는지 확인
2. 가상환경이 활성화되어 있는지 확인
3. 의존성이 설치되어 있는지 확인

```bash
# 의존성 재설치
uv sync
# 또는
pip install -e .
```

### 뉴스 파일을 찾을 수 없는 경우

1. `NEWS_FILE` 환경 변수가 올바른 경로를 가리키는지 확인
2. 파일이 실제로 존재하는지 확인
3. 파일 권한이 올바른지 확인

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
