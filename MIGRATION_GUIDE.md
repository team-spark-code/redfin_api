# RedFin API 구조 마이그레이션 가이드

## 🔄 변경된 구조

### 기존 구조 → 새로운 구조
- `src/redfin_api/models.py` → `app/schemas/news.py`
- `src/redfin_api/config.py` → `app/core/config.py`
- `src/redfin_api/main.py` → `app/main.py`
- `src/redfin_api/load_data.py` → `app/utils/data_loader.py`

### 새로운 구조
```
app/
├── api/           # API 라우터
├── core/          # 핵심 설정
├── models/        # 데이터베이스 모델
├── schemas/       # Pydantic 스키마
├── services/      # 비즈니스 로직
├── utils/         # 유틸리티 함수
└── main.py        # FastAPI 앱
```

## 📝 Import 문 업데이트

### 기존 코드
```python
from src.redfin_api.models import NewsEntry
from src.redfin_api.config import MONGO_URI
```

### 새로운 코드
```python
from app.schemas.news import NewsEntry
from app.core.config import settings
```

## 🚀 실행 방법

### 새로운 실행 스크립트
```bash
python run_app.py
```

### 기존 실행 스크립트 (하위 호환성)
```bash
python run.py
```

## 🔧 문제 해결

### Import 오류 발생 시
1. 가상환경이 활성화되어 있는지 확인
2. `pip install -r requirements.txt` 실행
3. 프로젝트 루트에서 실행하고 있는지 확인

### 기존 코드 복원이 필요한 경우
```bash
# 백업에서 복원
cp -r backup_old_structure/src/redfin_api/* src/redfin_api/
```
