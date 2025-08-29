#!/bin/bash
# RedFin API Docker 이미지 빌드 스크립트

set -euo pipefail

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 스크립트 디렉토리로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# 기본값 설정
IMAGE_NAME="redfin-api"
IMAGE_TAG="latest"
BUILD_TARGET="production"
PUSH_IMAGE=false
DRY_RUN=false

# 도움말 함수
show_help() {
    cat << EOF
RedFin API Docker 이미지 빌드 스크립트

사용법: $0 [옵션]

옵션:
    -n, --name NAME      이미지 이름 (기본값: redfin-api)
    -t, --tag TAG        이미지 태그 (기본값: latest)
    -b, --build-target  빌드 타겟 (기본값: production)
    -p, --push          이미지 푸시 (기본값: false)
    -d, --dry-run       실제 빌드 없이 명령어만 출력
    -h, --help          이 도움말 표시

예시:
    $0                           # 기본 설정으로 빌드
    $0 -t v1.0.0               # 특정 태그로 빌드
    $0 -b builder -d           # 빌더 타겟으로 드라이런
    $0 -t v1.0.0 -p            # 빌드 후 푸시

EOF
}

# 명령행 인수 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -t|--tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        -b|--build-target)
            BUILD_TARGET="$2"
            shift 2
            ;;
        -p|--push)
            PUSH_IMAGE=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "알 수 없는 옵션: $1"
            show_help
            exit 1
            ;;
    esac
done

# 환경 확인
log_info "프로젝트 디렉토리: $PROJECT_DIR"
log_info "이미지 이름: $IMAGE_NAME"
log_info "이미지 태그: $IMAGE_TAG"
log_info "빌드 타겟: $BUILD_TARGET"
log_info "이미지 푸시: $PUSH_IMAGE"
log_info "드라이런: $DRY_RUN"

# Docker 설치 확인
if ! command -v docker &> /dev/null; then
    log_error "Docker가 설치되지 않았습니다."
    exit 1
fi

# Docker 데몬 실행 확인
if ! docker info &> /dev/null; then
    log_error "Docker 데몬이 실행되지 않았습니다."
    exit 1
fi

# 필수 파일 확인
if [[ ! -f "Dockerfile" ]]; then
    log_error "Dockerfile을 찾을 수 없습니다."
    exit 1
fi

if [[ ! -f "requirements.txt" ]]; then
    log_error "requirements.txt를 찾을 수 없습니다."
    exit 1
fi

# 빌드 명령어 구성
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"
BUILD_CMD="docker build --target ${BUILD_TARGET} -t ${FULL_IMAGE_NAME} ."

log_info "빌드 명령어: $BUILD_CMD"

if [[ "$DRY_RUN" == true ]]; then
    log_warning "드라이런 모드: 실제 빌드가 실행되지 않습니다."
    exit 0
fi

# 이미지 빌드
log_info "Docker 이미지 빌드 시작..."
if eval "$BUILD_CMD"; then
    log_success "이미지 빌드 완료: $FULL_IMAGE_NAME"
else
    log_error "이미지 빌드 실패"
    exit 1
fi

# 이미지 정보 출력
log_info "빌드된 이미지 정보:"
docker images "$IMAGE_NAME" | head -2

# 이미지 크기 정보
IMAGE_SIZE=$(docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" "$IMAGE_NAME" | grep "$IMAGE_TAG" | awk '{print $3}')
log_info "이미지 크기: $IMAGE_SIZE"

# 이미지 푸시 (요청된 경우)
if [[ "$PUSH_IMAGE" == true ]]; then
    log_info "Docker Hub에 이미지 푸시 중..."
    if docker push "$FULL_IMAGE_NAME"; then
        log_success "이미지 푸시 완료: $FULL_IMAGE_NAME"
    else
        log_error "이미지 푸시 실패"
        exit 1
    fi
fi

log_success "모든 작업이 완료되었습니다!"
