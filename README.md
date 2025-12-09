# RedFin API

AI RSS News API Service - FastAPI 기반 뉴스 추천 및 분석 서비스

## 📋 개요

RedFin API는 RSS 뉴스 피드를 수집, 분석, 제공하는 RESTful API 서비스입니다.<br>
클린 아키텍처 원칙을 따르며, Repository 패턴과 의존성 주입을 통해<br>
유지보수성과 테스트 용이성을 확보한 FastAPI 기반 애플리케이션입니다.

### 주요 특징

- **클린 아키텍처**: Repository 패턴, 의존성 주입, 계층 분리
- **다중 백엔드 지원**: 파일(JSONL) 및 MongoDB 백엔드
- **API 버전 관리**: `/api/v1/` 구조로 버전별 엔드포인트 관리
- **스마트 검색**: 텍스트 검색, 소스/그룹 필터링, 신선도 점수 기반 정렬
- **자동 문서화**: Swagger UI 및 ReDoc 제공

### 기술 스택

- **프레임워크**: FastAPI 0.115+
- **데이터베이스**: MongoDB (Motor 비동기 드라이버)
- **검증**: Pydantic 2.8+
- **서버**: Uvicorn
- **테스트**: Pytest

## 🏗️ 프로젝트 구조

```
redfin_api/
├── app/                    # FastAPI 애플리케이션
│   ├── api/v1/endpoints/  # API 엔드포인트
│   ├── repositories/      # 데이터 접근 계층
│   ├── services/          # 비즈니스 로직
│   ├── core/              # 설정 및 의존성 컨테이너
│   ├── schemas/           # Pydantic 스키마
│   └── models/            # 도메인 모델
├── docs/                  # 문서
├── scripts/               # 유틸리티 스크립트
├── tests/                 # 테스트 코드
└── run.py                # 애플리케이션 실행 스크립트
```

상세한 구조는 [개발 가이드](#-개발-가이드) 섹션을 참고하세요.

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
# 방법 1: Python 스크립트로 실행 (권장)
python run.py

# 방법 2: uvicorn으로 직접 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔌 API 엔드포인트

### 뉴스 API (`/api/v1/news`)

- `GET /` - 뉴스 목록 조회 (검색, 필터링, 정렬 지원)
- `GET /description` - 뉴스 description 응답 형식으로 조회
- `GET /health` - 헬스체크
- `GET /sources` - 사용 가능한 뉴스 소스 목록
- `GET /groups` - 사용 가능한 뉴스 그룹 목록

### 기사 API (`/api/v1/articles`)

- `GET /` - 기사 목록 조회 (페이지네이션, 검색, 태그 필터)
- `POST /` - 새 기사 생성
- `GET /{id}` - ID로 기사 조회
- `PUT /{id}` - 기사 업데이트
- `DELETE /{id}` - 기사 삭제
- `GET /categories` - 카테고리 목록 조회
- `GET /category/{category}` - 카테고리별 기사 조회

### 기본 엔드포인트

- `GET /` - 루트 정보
- `GET /health` - 기본 헬스체크

## 📚 API 문서

서버 실행 후 다음 URL에서 상세한 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

더 자세한 API 문서는 [docs/api.md](docs/api.md)를 참고하세요.

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

자세한 Docker 빌드 및 실행 방법은 [빌드 가이드](docs/build.md)를 참고하세요.

```bash
# Docker 이미지 빌드
docker build --target production -t redfin-api:latest .

# Docker Compose로 실행
docker-compose up -d

# 컨테이너 직접 실행
docker run -p 8000:8000 redfin-api:latest
```

## 🧪 테스트

```bash
# 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_news_api.py
```

## 📝 개발 가이드

### 아키텍처 개요

이 프로젝트는 **클린 아키텍처** 원칙을 따릅니다:

```
┌─────────────────────────────────────────┐
│         API Layer (v1/endpoints)        │
│         - HTTP 요청/응답 처리            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Service Layer                   │
│         - 비즈니스 로직                  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Repository Layer                │
│         - 데이터 접근 계층               │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Database (MongoDB/File)         │
└─────────────────────────────────────────┘
```

**핵심 원칙:**
- **Repository 패턴**: 데이터 접근 계층 분리 (`app/repositories/`)
- **의존성 주입**: `app/core/container.py`를 통한 중앙화된 의존성 관리
- **API 버전 관리**: `app/api/v1/` 구조로 버전별 엔드포인트 관리
- **비동기 처리**: 모든 서비스 메서드가 async/await 사용

### 상세 프로젝트 구조

```
app/
├── api/
│   ├── v1/
│   │   ├── endpoints/      # 엔드포인트 구현
│   │   │   ├── news.py
│   │   │   └── articles.py
│   │   └── api.py          # 라우터 통합
│   └── deps.py             # 의존성 주입 함수
├── repositories/           # 데이터 접근 계층
│   ├── base.py            # BaseRepository
│   ├── news_repository.py
│   └── article_repository.py
├── services/              # 비즈니스 로직
│   ├── news_service.py
│   └── article_service.py
├── core/                  # 핵심 설정
│   ├── config.py          # 애플리케이션 설정
│   ├── database.py        # 데이터베이스 연결
│   ├── container.py       # 의존성 컨테이너
│   └── exceptions.py      # 커스텀 예외
├── schemas/               # Pydantic 스키마
├── models/                # 도메인 모델
└── main.py                # FastAPI 앱 진입점
```

### 새로운 API 엔드포인트 추가

1. `app/api/v1/endpoints/` 디렉토리에 새 엔드포인트 파일 생성
2. `app/api/v1/api.py`에 라우터 등록
3. 필요한 스키마를 `app/schemas/`에 추가
4. Repository를 `app/repositories/`에 구현
5. 비즈니스 로직을 `app/services/`에 구현
6. `app/api/deps.py`에 의존성 주입 함수 추가

### 새로운 서비스 추가

1. `app/repositories/`에 Repository 구현
2. `app/services/` 디렉토리에 서비스 클래스 생성
3. `app/core/container.py`에 팩토리 메서드 추가
4. `app/api/deps.py`에 의존성 주입 함수 추가
5. 필요한 의존성을 `requirements.txt`에 추가
6. 설정을 `app/core/config.py`에 추가

### API 사용 예제

API 사용 예제는 [`scripts/example_usage.py`](scripts/example_usage.py)를 참고하세요.

## 📚 문서

상세한 문서는 [`docs/`](docs/) 디렉토리에서 확인할 수 있습니다:

- [🏗️ 빌드 가이드](docs/build.md) - Docker 이미지 빌드 및 배포 방법
- [📖 API 문서](docs/api.md) - API 기능 상세 설명 및 엔드포인트 명세
- [🔄 마이그레이션 가이드](docs/migration.md) - 기존 구조에서 새 구조로 마이그레이션
- [🧪 테스트 리포트](docs/test-report.md) - 테스트 결과 및 커버리지

## 📊 성능 최적화

- 데이터 캐싱으로 반복 쿼리 최적화
- MongoDB 인덱싱 권장
- 대용량 데이터 처리를 위한 배치 처리 지원
