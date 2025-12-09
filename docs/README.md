# RedFin API 문서

이 디렉토리에는 RedFin API 프로젝트의 상세 문서가 포함되어 있습니다.

## 📚 문서 목록

### [빌드 가이드](build.md)
Docker 이미지 빌드, 컨테이너 실행, 배포 방법에 대한 상세 가이드입니다.
- Docker 이미지 빌드
- Docker Compose 실행
- 컨테이너 관리
- 문제 해결

### [API 문서](api.md)
API 기능, 엔드포인트, 사용법에 대한 상세 설명입니다.
- 뉴스 API (`/api/v1/news`)
- 기사 API (`/api/v1/articles`)
- 클린 아키텍처 구조 설명
- 사용 예제

### [마이그레이션 가이드](migration.md)
기존 프로젝트 구조에서 새로운 클린 아키텍처 구조로 마이그레이션하는 방법입니다.
- ⚠️ 이미 완료된 마이그레이션 가이드
- 구조 변경 내역
- Import 문 업데이트

### [테스트 리포트](test-report.md)
테스트 실행 결과, 커버리지, 성능 지표 등 테스트 관련 정보입니다.
- 단위 테스트 결과
- 통합 테스트 결과
- 성능 테스트

## 🏗️ 아키텍처

현재 프로젝트는 **클린 아키텍처**를 따릅니다:

```
app/
├── api/v1/endpoints/  # API 엔드포인트
├── repositories/      # 데이터 접근 계층
├── services/          # 비즈니스 로직
├── core/              # 설정 및 의존성 컨테이너
├── schemas/           # Pydantic 스키마
└── models/            # 도메인 모델
```

## 🔗 빠른 링크

- [메인 README](../README.md)
- [프로젝트 루트](../)
- [API 사용 예제](../scripts/example_usage.py)

