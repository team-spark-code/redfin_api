#!/usr/bin/env python3
"""
RedFin API 구조 마이그레이션 스크립트

기존 src/redfin_api/ 구조에서 새로운 app/ 구조로 마이그레이션
"""
import os
import shutil
import sys
from pathlib import Path


def backup_old_structure():
    """기존 구조 백업"""
    backup_dir = Path("backup_old_structure")
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    
    backup_dir.mkdir(exist_ok=True)
    
    # src/redfin_api/ 백업
    if Path("src").exists():
        shutil.copytree("src", backup_dir / "src")
        print(f"✅ 기존 src/ 구조를 {backup_dir}/src/에 백업했습니다")
    
    # 기존 파일들 백업
    old_files = ["main.py", "models.py", "config.py", "load_data.py"]
    for file in old_files:
        if Path(file).exists():
            shutil.copy2(file, backup_dir / file)
            print(f"✅ {file}을 {backup_dir}/{file}에 백업했습니다")
    
    return backup_dir


def cleanup_old_structure():
    """기존 구조 정리"""
    # src/redfin_api/ 디렉토리 정리
    if Path("src/redfin_api").exists():
        shutil.rmtree("src/redfin_api")
        print("🗑️  기존 src/redfin_api/ 디렉토리를 정리했습니다")
    
    # src/ 디렉토리가 비어있으면 제거
    if Path("src").exists() and not any(Path("src").iterdir()):
        Path("src").rmdir()
        print("🗑️  빈 src/ 디렉토리를 제거했습니다")
    
    # 기존 파일들 정리
    old_files = ["main.py", "models.py", "config.py", "load_data.py"]
    for file in old_files:
        if Path(file).exists():
            Path(file).unlink()
            print(f"🗑️  {file}을 제거했습니다")


def verify_new_structure():
    """새로운 구조 검증"""
    required_dirs = [
        "app",
        "app/api",
        "app/core", 
        "app/models",
        "app/schemas",
        "app/services",
        "app/utils"
    ]
    
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/core/config.py",
        "app/schemas/news.py",
        "app/services/news_service.py",
        "app/utils/data_loader.py",
        "app/api/news.py"
    ]
    
    print("\n🔍 새로운 구조 검증 중...")
    
    # 디렉토리 확인
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ (누락)")
            return False
    
    # 파일 확인
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (누락)")
            return False
    
    return True


def create_migration_guide():
    """마이그레이션 가이드 생성"""
    guide_content = """# RedFin API 구조 마이그레이션 가이드

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

### 실행 스크립트
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
"""
    
    with open("MIGRATION_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(guide_content)
    
    print("📝 MIGRATION_GUIDE.md 파일을 생성했습니다")


def main():
    """메인 마이그레이션 함수"""
    print("🚀 RedFin API 구조 마이그레이션을 시작합니다...")
    
    # 1. 기존 구조 백업
    backup_dir = backup_old_structure()
    
    # 2. 기존 구조 정리
    cleanup_old_structure()
    
    # 3. 새로운 구조 검증
    if not verify_new_structure():
        print("\n❌ 새로운 구조 검증에 실패했습니다")
        print(f"백업된 파일들은 {backup_dir}/ 에 있습니다")
        return False
    
    # 4. 마이그레이션 가이드 생성
    create_migration_guide()
    
    print("\n🎉 마이그레이션이 완료되었습니다!")
    print(f"📁 백업된 파일들: {backup_dir}/")
    print("📖 MIGRATION_GUIDE.md 파일을 참고하세요")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  마이그레이션이 중단되었습니다")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 마이그레이션 중 오류가 발생했습니다: {e}")
        sys.exit(1)
