# Redfin API 빌드

본 문서는 Redfin API를 빌드하는 방법을 단계적으로 설명합니다.

docker 환경을 설치하고 아래 작업을 진행해주세요.

## 0. 전체 워크플로우
```bash
cd redfin_api
docker build --target production -t redfin-api:latest .
docker stop redfin-api 2>/dev/null || true
docker rm redfin-app 2>/dev/null || true
docker-compose up -d
docker ps
curl http://localhost:8000/health
docker-compose logs -f redfin-api
```



## 1. 이미지 빌드
이미지 빌드란 컨테이너 상 필요한 의존성을 명세한 Dockerfile를 기반으로 이미지를 빌드하는 과정을 의미합니다.

빌드 시 고려사항:
1. `--no-cache`
    - 도커 빌드 과정에서 이전에 저장된 레이어 캐시를 사용하지 않고, 모든 단계를 새로 실행하겠다는 의미
    - 일반 빌드의 경우 Dockerfile의 각 단계(layer)를 실행할 때, 같은 명령과 같은 입력(파일/환경)이 있다면
      이전 빌드 결과를 재사용합니다.
    - 이를 통해 항상 최신 패키지를 받아오고, 캐시 문제(오래된 결과 사용)을 방지합니다.
    - 단, 빌드 과정을 전부 거치기에 속도가 느리고, 네트워크 트래픽이 증가합니다.
2. `--progress-plain`
    - Docker 18.09 이후의 `BuildKit` 기반 빌드에서는 로그가 깔끔하게 단일 줄로 출력
    - 이전 로그 방식을 활성화하여 더 많은 상세 빌드 이력 제공
3. multi-stage build
4. buildkit 사용


이미지 태그 네이밍 예시: `redfin-api:0.1.0`, `redfin-api:latest`

이미지 태그 업데이트 원칙:
    - 0.1.0 -> 0.1.0 (동일 버전)
    - 0.1.0 -> 0.1.1 (버전 업데이트)
    - 0.1.0 -> 0.2.0 (메이저 버전 업데이트) → 0.2.0 이미지 빌드
    - 0.1.0 -> 1.0.0 (마이너 버전 업데이트) → 1.0.0 이미지 빌드
    - 0.1.0 -> latest (최신 버전)


### 기본 빌드
```bash
# Docker 이미지 빌드
cd redfin_api
docker build --target production -t redfin-api:latest .

# 버전 태그 지정
docker build --target production -t redfin-api:0.1.0 .

# 여러 태그 동시 생성
docker build --target production -t redfin-api:latest -t redfin-api:0.1.0 .

# 빌드 캐시 사용 안함
docker build --target production -t redfin-api:latest --no-cache .
``` 

### 이미지 관리
```bash
# 이미지 태그
docker tag redfin-api:0.1.0 redfin-api:latest
docker tag redfin-api:latest sungminwoo0612/redfin-api:latest 
docker tag redfin-api:latest sungminwoo0612/redfin-api:0.1.0

# 이미지 푸시
docker push sungminwoo0612/redfin-api:latest
docker push sungminwoo0612/redfin-api:0.1.0

# 이미지 풀
docker pull sungminwoo0612/redfin-api:latest
```

## 2. 컨테이너 실행
### Docker Compose로 실행
```bash
# 프로덕션 환경 실행
docker-compose up -d

# 백그라운드 실행하면서 로그 확인
docker-compose up -d && docker-compose logs -f

# 개발 환경 실행 (포트 8001 사용)
docker-compose --profile dev up -d redfin-api-dev
``` 
### Docker 명령어로 직접 실행
```bash
# 기본 실행
docker run -d --name redfin-api -p 8000:8000 redfin-api:latest

# 환경변수와 볼륨 마운트
docker run -d \
    --name redfin-api \
    -p 8000:8000 \
    -e API_HOST=0.0.0.0 \
    -e API_PORT=8000 \
    -v ${pwd}/data:/app/data:ro \
    redfin-api:latest
```

## 3. 상태 확인
### 컨테이너 상태
```bash
# 실행 중인 컨테이너 확인
docker ps

# 모든 컨테이너 확인 (중지된 것 포함)
docker ps -a

# 특정 컨테이너 정보
docker inspect redfin-api
```

### 로그 확인
```bash
# 컨테이너 로그 확인
docker logs redfin-api

# 실시간 로그 모니터링
docker logs -f redfin-api

# 마지막 50줄 로그
docker logs --tail 50 redfin-api
```

### API 상태 확인
```bash
# 헬스체크
curl http://localhost:8000/health

# API 문서 접근
curl http://localhost:8000/docs

# 포트 확인
netstat -tlnp | grep 8000
```

## 4. 컨테이너 관리
### 시작/중지/재시작
```bash
# 컨테이너 시작
docker start redfin-api

# 컨테이너 중지
docker stop redfin-api

# 컨테이너 재시작
docker restart redfin-api
```

### 제거
```bash
# 컨테이너 중지 후 제거
docker stop redfin-api && docker rm redfin-api

# 강제 제거 (실행 중인 컨테이너도)
docker rm -f redfin-api
```

## 5. 이미지 관리
### 이미지 확인
```bash
# 빌드된 이미지 확인
docker images redfin-api

# 이미지 상세 정보
docker inspect redfin-api:latest

```

### 이미지 제거
```bash
# 특정 이미지 제거
docker rmi redfin-api:latest

# 사용하지 않는 이미지 정리
docker image prune

# 모든 이미지 정리 (주의!)
docker image prune -a
```

## 6. 문제 해결
### 빌드 오류 시
```bash
# 캐시 없이 빌드
docker build --no-cache --target production -t redfin-api:latest .

# 상세한 빌드 로그
docker build --progress=plain --target production -t redfin-api:latest .
```

### 컨테이너 실행 오류 시
```bash
# 컨테이너 로그 확인
docker logs redfin-api

# 컨테이너 내부 삽입
docker exec -it redfin-api bash

# 컨테이너 재시작
docker restart redfin-api
```

### 포트 충돌 시
```bash
# 포트 사용 확인 
netstat -ntlp | grep 8000

# 다른 포트로 실행
docker run -d --name redfin-api -p 8001:8000 redfin-api:latest
```
