# RedFin API

AI RSS News API Service - FastAPI 기반 뉴스 추천 및 분석 서비스

## 🏗️ 프로젝트 구조

```
redfin_api/
├── app/                    # FastAPI 애플리케이션
│   ├── api/               # API 라우터
│   │   └── news.py        # 뉴스 관련 엔드포인트
│   ├── core/              # 핵심 설정 및 의존성
│   │   └── config.py      # 애플리케이션 설정
│   ├── models/            # 데이터베이스 모델
│   ├── schemas/           # Pydantic 스키마
│   │   └── news.py        # 뉴스 관련 스키마
│   ├── services/          # 비즈니스 로직
│   │   └── news_service.py # 뉴스 서비스
│   ├── utils/             # 유틸리티 함수
│   │   └── data_loader.py # 데이터 로더
│   ├── __init__.py
│   └── main.py            # FastAPI 앱 메인
├── data/                  # 데이터 파일
├── tests/                 # 테스트 코드
├── .env                   # 환경 변수
├── requirements.txt       # Python 의존성
├── run_app.py            # 애플리케이션 실행 스크립트
└── README.md
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 또는
.venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 필요한 설정을 추가하세요:

```env
# 백엔드 설정
BACKEND=FILE  # FILE 또는 MONGO

# 파일 백엔드 설정
NEWS_FILE=data/all_entries_20250825_025249.jsonl

# MongoDB 백엔드 설정 (선택사항)
MONGO_URI=mongodb://localhost:27017
MONGO_DB=redfin
MONGO_COL=news

# API 서버 설정
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

# CORS 설정
CORS_ORIGINS=*
```

### 3. 애플리케이션 실행

```bash
# 방법 1: Python 스크립트로 실행
python run_app.py

# 방법 2: uvicorn으로 직접 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 방법 3: 기존 run.py 사용 (하위 호환성)
python run.py
```

## 📚 API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API 엔드포인트

### 뉴스 API (`/api/v1/news`)

- `GET /` - 뉴스 목록 조회
- `GET /description` - 뉴스 description 응답 형식으로 조회
- `GET /health` - 헬스체크
- `GET /sources` - 사용 가능한 뉴스 소스 목록
- `GET /groups` - 사용 가능한 뉴스 그룹 목록

### 기본 엔드포인트

- `GET /` - 루트 정보
- `GET /health` - 기본 헬스체크

## 🔧 주요 기능

### 1. 다중 백엔드 지원
- **파일 백엔드**: JSONL 파일에서 뉴스 데이터 로드
- **MongoDB 백엔드**: MongoDB에서 뉴스 데이터 조회

### 2. 스마트 검색 및 필터링
- 텍스트 기반 검색 (제목, 요약, 본문)
- 소스별, 그룹별 필터링
- 신선도 점수 기반 정렬

### 3. 캐싱 시스템
- 5분간 데이터 캐싱
- 새로고침 옵션으로 캐시 무효화

### 4. 데이터 검증
- Pydantic 스키마를 통한 데이터 검증
- 필수 필드 확인 및 오류 처리

## 🐳 Docker 실행

```bash
# Docker 이미지 빌드
docker build -t redfin-api .

# 컨테이너 실행
docker run -p 8000:8000 redfin-api
```

## 🧪 테스트

```bash
# 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_news_api.py
```

## 📝 개발 가이드

### 새로운 API 엔드포인트 추가

1. `app/api/` 디렉토리에 새 라우터 파일 생성
2. `app/main.py`에 라우터 등록
3. 필요한 스키마를 `app/schemas/`에 추가
4. 비즈니스 로직을 `app/services/`에 구현

### 새로운 서비스 추가

1. `app/services/` 디렉토리에 서비스 클래스 생성
2. 필요한 의존성을 `requirements.txt`에 추가
3. 설정을 `app/core/config.py`에 추가

## 🔄 마이그레이션 가이드

### 기존 코드에서 새 구조로

기존 `src/redfin_api/` 구조에서 새로운 `app/` 구조로 마이그레이션되었습니다:

- `models.py` → `app/schemas/news.py`
- `config.py` → `app/core/config.py`
- `main.py` → `app/main.py`
- `load_data.py` → `app/utils/data_loader.py`

기존 import 문을 새로운 경로로 업데이트하세요.

## 📊 성능 최적화

- 데이터 캐싱으로 반복 쿼리 최적화
- MongoDB 인덱싱 권장
- 대용량 데이터 처리를 위한 배치 처리 지원

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 있거나 질문이 있으시면 이슈를 생성해 주세요.
