# RedFin API 문서

## 📚 API 개요

RedFin API는 FastAPI 기반의 뉴스 및 기사 관리 API 서비스입니다.

## 🔌 API 엔드포인트

### 뉴스 API (`/api/v1/news`)

#### `GET /api/v1/news/`
뉴스 목록 조회

**쿼리 파라미터:**
- `q` (optional): 검색어
- `source` (optional): 특정 소스 필터
- `group` (optional): 특정 그룹 필터
- `limit` (default: 20): 조회 개수 (1-100)
- `offset` (default: 0): 오프셋
- `sort` (default: "fresh"): 정렬 방식 ("fresh" | "time")
- `refresh` (default: false): 캐시 새로고침

**응답:**
```json
[
  {
    "source": "OpenAI Blog",
    "title": "Article Title",
    "link": "https://example.com/article",
    "published": "2025-08-25T10:00:00",
    "summary": "Article summary",
    "authors": ["Author Name"],
    "tags": ["tag1", "tag2"]
  }
]
```

#### `GET /api/v1/news/description`
뉴스 description 응답 형식으로 조회

**쿼리 파라미터:** 위와 동일

**응답:**
```json
{
  "success": true,
  "count": 10,
  "total": 100,
  "data": [
    {
      "guid": "unique-id",
      "source": "OpenAI Blog",
      "title": "Article Title",
      "link": "https://example.com/article",
      "article_text": "Full article text",
      "summary": "Article summary",
      "tags": ["tag1", "tag2"],
      "content_type": "NEWS",
      "language": "ENGLISH",
      "readability_score": 0.85,
      "key_entities": ["entity1", "entity2"],
      "processed_at": "2025-08-25T10:00:00",
      "text_length": 1500
    }
  ]
}
```

#### `GET /api/v1/news/health`
헬스체크

**응답:**
```json
{
  "ok": true,
  "count": 1000,
  "backend": "MONGO",
  "version": "0.2.0"
}
```

#### `GET /api/v1/news/sources`
사용 가능한 뉴스 소스 목록

**응답:**
```json
{
  "sources": ["OpenAI Blog", "Google AI Blog", ...],
  "count": 25
}
```

#### `GET /api/v1/news/groups`
사용 가능한 뉴스 그룹 목록

**응답:**
```json
{
  "groups": ["frontier_lab", "research", ...],
  "count": 5
}
```

### 기사 API (`/api/v1/articles`)

#### `GET /api/v1/articles/`
기사 목록 조회

**쿼리 파라미터:**
- `page` (default: 1): 페이지 번호
- `size` (default: 10): 페이지 크기 (1-200)
- `search` (optional): 검색어 (제목, 요약, 본문, 키워드)
- `tags` (optional): 태그 필터 (배열)
- `include_news` (default: false): news 컬렉션도 포함하여 조회

**응답:**
```json
{
  "items": [
    {
      "id": "article-id",
      "title": "Article Title",
      "summary": "Article summary",
      "url": "https://example.com/article",
      "keywords": ["keyword1", "keyword2"],
      "category": "Research",
      "body": "Article body",
      "published_at": "2025-08-25T10:00:00",
      "tags": ["tag1", "tag2"],
      "created_at": "2025-08-25T10:00:00",
      "updated_at": "2025-08-25T10:00:00"
    }
  ],
  "total": 100,
  "page": 1,
  "size": 10
}
```

#### `POST /api/v1/articles/`
새 기사 생성

**요청 본문:**
```json
{
  "Title": "Article Title",
  "Summary": "Article summary",
  "URL": "https://example.com/article",
  "keywords": "['keyword1', 'keyword2']",
  "category": "Research",
  "body": "Article body",
  "published_at": "2025-08-25T10:00:00",
  "tags": ["tag1", "tag2"]
}
```

#### `GET /api/v1/articles/{article_id}`
ID로 기사 조회

#### `PUT /api/v1/articles/{article_id}`
기사 업데이트

#### `DELETE /api/v1/articles/{article_id}`
기사 삭제

#### `GET /api/v1/articles/categories`
모든 카테고리 목록 조회 (각 카테고리별 기사 수 포함)

#### `GET /api/v1/articles/category/{category}`
특정 카테고리의 기사 조회

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
- Pydantic 스키마를 통한 자동 입력 검증
- 필수 필드 확인 및 오류 처리

### 5. 검색 최적화
- 제목, 요약, 태그에서 텍스트 검색
- 소스별 필터링으로 검색 범위 제한
- 페이지네이션으로 대용량 데이터 처리

## 🔒 보안

### CORS 설정
- 기본적으로 모든 도메인 허용 (`CORS_ORIGINS=*`)
- 프로덕션 환경에서는 특정 도메인만 허용하도록 설정
- 환경 변수 `CORS_ORIGINS`로 제어

### 입력 검증
- Pydantic 모델을 통한 자동 입력 검증
- 쿼리 파라미터 범위 제한 (limit: 1-100)
- 정렬 방식 패턴 검증

## 📖 사용 예제

API 사용 예제는 [`scripts/example_usage.py`](../scripts/example_usage.py)를 참고하세요.
