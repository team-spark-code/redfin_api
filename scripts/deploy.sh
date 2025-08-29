#!/bin/bash
# RedFin API 컨테이너 배포 스크립트

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
SERVICE_NAME="redfin-api"
COMPOSE_FILE="docker-compose.yml"
BUILD_IMAGE=false
FORCE_RESTART=false
DRY_RUN=false

# 도움말 함수
show_help() {
    cat << EOF
RedFin API 컨테이너 배포 스크립트

사용법: $0 [옵션]

옵션:
    -s, --service NAME   서비스 이름 (기본값: redfin-api)
    -f, --file FILE      Compose 파일 (기본값: docker-compose.yml)
    -b, --build          이미지 재빌드
    -r, --restart        강제 재시작
    -d, --dry-run        실제 배포 없이 명령어만 출력
    -h, --help           이 도움말 표시

예시:
    $0                    # 기본 배포
    $0 -b                # 이미지 재빌드 후 배포
    $0 -r                # 강제 재시작
    $0 -b -r             # 재빌드 후 강제 재시작
    $0 -d                # 드라이런 모드

EOF
}

# 명령행 인수 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--service)
            SERVICE_NAME="$2"
            shift 2
            ;;
        -f|--file)
            COMPOSE_FILE="$2"
            shift 2
            ;;
        -b|--build)
            BUILD_IMAGE=true
            shift
            ;;
        -r|--restart)
            FORCE_RESTART=true
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
log_info "서비스 이름: $SERVICE_NAME"
log_info "Compose 파일: $COMPOSE_FILE"
log_info "이미지 재빌드: $BUILD_IMAGE"
log_info "강제 재시작: $FORCE_RESTART"
log_info "드라이런: $DRY_RUN"

# Docker Compose 설치 확인
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose가 설치되지 않았습니다."
    exit 1
fi

# Docker 데몬 실행 확인
if ! docker info &> /dev/null; then
    log_error "Docker 데몬이 실행되지 않았습니다."
    exit 1
fi

# Compose 파일 확인
if [[ ! -f "$COMPOSE_FILE" ]]; then
    log_error "Compose 파일을 찾을 수 없습니다: $COMPOSE_FILE"
    exit 1
fi

# 기존 컨테이너 상태 확인
log_info "기존 컨테이너 상태 확인 중..."
if docker-compose -f "$COMPOSE_FILE" ps | grep -q "$SERVICE_NAME"; then
    log_info "기존 서비스가 실행 중입니다."
    CONTAINER_STATUS=$(docker-compose -f "$COMPOSE_FILE" ps "$SERVICE_NAME" | tail -n +2 | awk '{print $6}')
    log_info "컨테이너 상태: $CONTAINER_STATUS"
else
    log_info "기존 서비스가 실행되지 않았습니다."
fi

# 배포 명령어 구성
if [[ "$BUILD_IMAGE" == true ]]; then
    DEPLOY_CMD="docker-compose -f $COMPOSE_FILE up -d --build $SERVICE_NAME"
    log_info "이미지 재빌드 모드로 배포합니다."
else
    DEPLOY_CMD="docker-compose -f $COMPOSE_FILE up -d $SERVICE_NAME"
fi

if [[ "$FORCE_RESTART" == true ]]; then
    RESTART_CMD="docker-compose -f $COMPOSE_FILE restart $SERVICE_NAME"
    log_info "강제 재시작 모드로 배포합니다."
fi

log_info "배포 명령어: $DEPLOY_CMD"
if [[ "$FORCE_RESTART" == true ]]; then
    log_info "재시작 명령어: $RESTART_CMD"
fi

if [[ "$DRY_RUN" == true ]]; then
    log_warning "드라이런 모드: 실제 배포가 실행되지 않습니다."
    exit 0
fi

# 기존 서비스 중지 (필요한 경우)
if [[ "$FORCE_RESTART" == true ]] && docker-compose -f "$COMPOSE_FILE" ps | grep -q "$SERVICE_NAME"; then
    log_info "기존 서비스를 중지합니다..."
    docker-compose -f "$COMPOSE_FILE" stop "$SERVICE_NAME"
fi

# 서비스 배포
log_info "서비스 배포 시작..."
if eval "$DEPLOY_CMD"; then
    log_success "서비스 배포 완료"
else
    log_error "서비스 배포 실패"
    exit 1
fi

# 강제 재시작 (요청된 경우)
if [[ "$FORCE_RESTART" == true ]]; then
    log_info "서비스 재시작 중..."
    if eval "$RESTART_CMD"; then
        log_success "서비스 재시작 완료"
    else
        log_error "서비스 재시작 실패"
        exit 1
    fi
fi

# 배포 후 상태 확인
log_info "배포 후 서비스 상태 확인 중..."
sleep 5

if docker-compose -f "$COMPOSE_FILE" ps | grep -q "$SERVICE_NAME"; then
    log_success "서비스가 성공적으로 실행되었습니다."
    
    # 컨테이너 정보 출력
    log_info "컨테이너 정보:"
    docker-compose -f "$COMPOSE_FILE" ps "$SERVICE_NAME"
    
    # 로그 확인
    log_info "최근 로그 (마지막 10줄):"
    docker-compose -f "$COMPOSE_FILE" logs --tail=10 "$SERVICE_NAME"
    
    # 포트 확인
    log_info "포트 매핑:"
    docker port "$(docker-compose -f "$COMPOSE_FILE" ps -q "$SERVICE_NAME")"
    
else
    log_error "서비스 실행에 실패했습니다."
    log_info "로그 확인:"
    docker-compose -f "$COMPOSE_FILE" logs "$SERVICE_NAME"
    exit 1
fi

log_success "배포가 완료되었습니다!"
