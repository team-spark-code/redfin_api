# RedFin API Makefile

.PHONY: help install install-dev test lint format clean run run-dev docker-build docker-run

help: ## 도움말 표시
	@echo "사용 가능한 명령어:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 프로덕션 의존성 설치
	uv sync

install-dev: ## 개발 의존성 설치
	uv sync --extra dev

test: ## 테스트 실행
	pytest tests/ -v

test-coverage: ## 테스트 커버리지 실행
	pytest tests/ --cov=src/redfin_api --cov-report=html --cov-report=term

lint: ## 코드 린팅
	flake8 src/ tests/
	mypy src/

type-check: ## 타입 체크
	mypy src/

format: ## 코드 포맷팅
	black src/ tests/
	isort src/ tests/

format-check: ## 코드 포맷팅 검사
	black --check src/ tests/
	isort --check-only src/ tests/

clean: ## 임시 파일 정리
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/

run: ## 서버 실행
	python run.py

run-dev: ## 개발 모드로 서버 실행
	API_RELOAD=true python run.py

docker-build: ## Docker 이미지 빌드
	docker build -t redfin-api .

docker-run: ## Docker 컨테이너 실행
	docker run -p 8000:8000 redfin-api

check: format-check lint test ## 모든 검사 실행

pre-commit: format lint test ## 커밋 전 검사
