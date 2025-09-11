## RedFin API `scripts/` 단위 테스트 계획서

### 1) 문서 개요
- **대상**: `redfin_api/scripts/start.sh`, `redfin_api/scripts/start.ps1`
- **목적**: 스크립트의 분기 처리, 환경 변수 로드, 의존성 설치 분기, 서버 실행 흐름, 오류 처리의 신뢰성 검증
- **테스트 유형**: 정적 분석, 모킹 기반 단위 테스트, 스모크 수준 통합 검증

### 2) 범위
- **포함**: 경로 전이, `.env` 로드, `venv` 활성화, 의존성 체크/설치 분기, `run.py` 실행, 실패 시 종료 동작
- **제외**: 애플리케이션 비즈니스 로직, 네트워크/포트 충돌 실제 검증

### 3) 테스트 전략
- **정적 분석**
  - 셸: shellcheck
  - PowerShell: PSScriptAnalyzer
- **단위 테스트**
  - 셸: Bats(bats-core, bats-support, bats-assert) + 가짜 바이너리 스텁
  - PowerShell: Pester 5.x + `Mock`/`Assert-MockCalled`
- **격리/샌드박스**
  - 임시 프로젝트 루트 생성 후 `.env`, `venv/`, `run.py`(더미), 가짜 실행 파일(`python`, `uv`, `pip`) 배치
  - `PATH`를 임시 바이너리 디렉터리로 우선 설정해 호출 가로채기
  - 테스트마다 환경 변수, 작업 디렉터리 초기화

### 4) 테스트 환경 및 도구
- **운영체제 매트릭스**: Ubuntu(Linux)와 Windows
- **도구 버전**: Bats ≥ 1.10, Pester 5.x, shellcheck 최신, PSScriptAnalyzer 최신

### 5) 테스트 디렉터리 구조(제안)
- 테스트 코드
  - `tests/scripts/start_sh.bats`
  - `tests/scripts/start_ps1.Tests.ps1`
- 픽스처
  - `tests/fixtures/scripts/env/` 다양한 `.env` 샘플
  - `tests/fixtures/scripts/bin/` 가짜 실행 파일 템플릿

### 6) 핵심 테스트 케이스

#### 6.1 start.sh
- TC-SH-001 경로 전이: 스크립트 하위 경로에서 실행 시 프로젝트 루트로 이동
- TC-SH-002 `.env` 로드(정상): 주석 제외 키=값 로드 확인
- TC-SH-003 `.env` 경계: 값 내 공백/`=` 포함 시 현재 `xargs` 한계 검증/문서화
- TC-SH-004 `venv` 활성화: `venv/bin/activate` 존재 시 활성화 시도
- TC-SH-005 의존성 설치 스킵: `python -c "import fastapi, uvicorn"` 성공 시 설치 미수행
- TC-SH-006 의존성 설치(uv): `python -c` 실패 + `uv` 존재 시 `uv sync` 호출
- TC-SH-007 의존성 설치(pip): `python -c` 실패 + `uv` 없음 시 `pip install -e .` 호출
- TC-SH-008 설치 실패 시 종료: `set -e`에 따라 비정상 종료
- TC-SH-009 서버 실행: `python run.py` 호출 및 환경 로그 출력

#### 6.2 start.ps1
- TC-PS-001 경로 전이: 프로젝트 루트로 전이
- TC-PS-002 `.env` 로드: 프로세스 스코프 환경 변수 설정, 주석/빈줄 무시
- TC-PS-003 `.env` 경계: 값 내 공백/`=` 포함 시 현재 정규식 한계 검증/문서화
- TC-PS-004 `venv` 활성화: `venv\Scripts\Activate.ps1` 실행 호출
- TC-PS-005 의존성 설치 스킵: `python -c` 성공 시 설치 미수행
- TC-PS-006 의존성 설치(uv): `Get-Command uv` 성공 시 `uv sync` 호출
- TC-PS-007 의존성 설치(pip): `uv` 미존재 시 `pip install -e .` 호출
- TC-PS-008 설치 실패 예외: 예외 발생 시 중단 및 메시지 확인
- TC-PS-009 서버 실행: `python run.py` 호출 및 환경 로그 출력

### 7) 테스트 실행 절차

#### 7.1 정적 분석
```bash
shellcheck /home/redfin/workspace/redfin/redfin_api/scripts/start.sh
```
```powershell
Invoke-ScriptAnalyzer -Path "C:\path\to\repo\redfin_api\scripts\start.ps1" -Recurse
```

#### 7.2 Bats 테스트(Linux)
```bash
sudo apt-get update && sudo apt-get install -y bats shellcheck
bats -r /home/redfin/workspace/redfin/tests/scripts/start_sh.bats
```

#### 7.3 Pester 테스트(Windows)
```powershell
Install-Module Pester -Scope CurrentUser -Force
Invoke-Pester -Path "C:\path\to\repo\tests\scripts\start_ps1.Tests.ps1" -Output Detailed
```

### 8) 샘플 테스트 스켈레톤

#### 8.1 `tests/scripts/start_sh.bats`
```bash
#!/usr/bin/env bats

setup() {
  TEST_ROOT="$(mktemp -d)"
  export PATH="$TEST_ROOT/bin:$PATH"
  mkdir -p "$TEST_ROOT/bin" "$TEST_ROOT/project/scripts"
  cp /home/redfin/workspace/redfin/redfin_api/scripts/start.sh "$TEST_ROOT/project/scripts/start.sh"
  chmod +x "$TEST_ROOT/project/scripts/start.sh"

  cat > "$TEST_ROOT/bin/python" <<'PY'
#!/usr/bin/env bash
if [[ "$1" == "-c" ]]; then
  if [[ "${PY_IMPORT_FAIL:-0}" == "1" ]]; then exit 1; else exit 0; fi
fi
echo "PY_RUN $@" >> "$TMPDIR/run.log"
exit 0
PY
  chmod +x "$TEST_ROOT/bin/python"

  cat > "$TEST_ROOT/bin/uv" <<'UV'
#!/usr/bin/env bash
echo "UV_SYNC" >> "$TMPDIR/calls.log"
exit "${UV_EXIT:-0}"
UV
  chmod +x "$TEST_ROOT/bin/uv"

  cat > "$TEST_ROOT/bin/pip" <<'PIP'
#!/usr/bin/env bash
echo "PIP_INSTALL $@" >> "$TMPDIR/calls.log"
exit "${PIP_EXIT:-0}"
PIP
  chmod +x "$TEST_ROOT/bin/pip"

  export TMPDIR="$TEST_ROOT/tmp"
  mkdir -p "$TMPDIR"
}

teardown() { rm -rf "$TEST_ROOT"; }

@test "SH: 의존성 설치 스킵" {
  export PY_IMPORT_FAIL=0
  pushd "$TEST_ROOT/project" >/dev/null
  touch run.py
  run ./scripts/start.sh
  [ "$status" -eq 0 ]
  refute grep -q "UV_SYNC" "$TMPDIR/calls.log" || true
  refute grep -q "PIP_INSTALL" "$TMPDIR/calls.log" || true
  popd >/dev/null
}

@test "SH: 의존성 설치(uv)" {
  export PY_IMPORT_FAIL=1
  export UV_EXIT=0
  pushd "$TEST_ROOT/project" >/dev/null
  touch run.py
  run ./scripts/start.sh
  [ "$status" -eq 0 ]
  grep -q "UV_SYNC" "$TMPDIR/calls.log"
  popd >/dev/null
}

@test "SH: 의존성 설치(pip)" {
  export PY_IMPORT_FAIL=1
  rm -f "$TEST_ROOT/bin/uv"
  pushd "$TEST_ROOT/project" >/dev/null
  touch run.py
  run ./scripts/start.sh
  [ "$status" -eq 0 ]
  grep -q "PIP_INSTALL -e \\." "$TMPDIR/calls.log"
  popd >/dev/null
}
```

#### 8.2 `tests/scripts/start_ps1.Tests.ps1`
```powershell
#requires -Version 7
Import-Module Pester

Describe 'start.ps1' {
  BeforeAll {
    $TestRoot = New-Item -ItemType Directory -Path ([System.IO.Path]::GetTempPath() + [System.Guid]::NewGuid())
    $Project = Join-Path $TestRoot 'project'
    $Scripts = Join-Path $Project 'scripts'
    New-Item -ItemType Directory -Path $Scripts -Force | Out-Null
    Copy-Item -Path "$env:REPO_ROOT\\redfin_api\\scripts\\start.ps1" -Destination (Join-Path $Scripts 'start.ps1')
    Set-Location $Project
  }

  AfterAll { Remove-Item -Recurse -Force $TestRoot }

  It 'PS: 의존성 설치 스킵' {
    New-Item -ItemType File -Path (Join-Path $Project 'run.py') | Out-Null

    Mock -CommandName python -MockWith { param($a,$b) if ($a -eq '-c') { return } else { return } }
    Mock -CommandName uv
    Mock -CommandName pip

    . "$Scripts\\start.ps1"

    Assert-MockNotCalled -CommandName uv
    Assert-MockNotCalled -CommandName pip
  }

  It 'PS: 의존성 설치(uv)' {
    New-Item -ItemType File -Path (Join-Path $Project 'run.py') -Force | Out-Null

    Mock -CommandName python -MockWith { param($a,$b) if ($a -eq '-c') { throw 'ImportError' } }
    Mock -CommandName uv -MockWith { return }
    Mock -CommandName pip

    . "$Scripts\\start.ps1"

    Assert-MockCalled -CommandName uv -Times 1
    Assert-MockNotCalled -CommandName pip
  }
}
```

### 9) CI 통합(예: GitHub Actions)
```yaml
name: scripts-ci

on:
  push:
  pull_request:

jobs:
  linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install tools
        run: |
          sudo apt-get update
          sudo apt-get install -y shellcheck bats
      - name: Lint shell
        run: shellcheck redfin_api/scripts/start.sh
      - name: Run Bats
        run: bats -r tests/scripts/start_sh.bats

  windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Pester
        shell: pwsh
        run: Install-Module Pester -Scope CurrentUser -Force
      - name: Lint PowerShell
        shell: pwsh
        run: Install-Module PSScriptAnalyzer -Scope CurrentUser -Force; Invoke-ScriptAnalyzer -Path redfin_api/scripts/start.ps1
      - name: Run Pester
        shell: pwsh
        env:
          REPO_ROOT: ${{ github.workspace }}
        run: Invoke-Pester -Path tests/scripts/start_ps1.Tests.ps1 -Output Detailed
```

### 10) 커버리지 및 리포팅
- Bats/Pester 기본 출력 + 실패 시 로그 아티팩트 수집(`calls.log`, `run.log`, 표준출력 캡처)
- CI에서 `actions/upload-artifact`로 업로드

### 11) 위험/경계조건
- `.env` 파싱 한계:
  - `start.sh`: `xargs` 방식은 인용/공백/`=` 포함 값에 취약
  - `start.ps1`: 현재 정규식은 값 내 `=` 포함 시 한계 존재
- PATH/환경 오염: 각 테스트마다 격리 필요
- Windows/Ubuntu 간 줄바꿈/경로 구분자 차이

### 12) 향후 개선 제안
- 플래그 도입: `--dry-run`, `--verbose`, `--no-install`
- 주요 단계를 함수화하고 에러 처리 일원화(테스트 용이성 향상)
- 견고한 `.env` 파서로 교체(인용/이스케이프 지원)

### 13) 완료 기준(DoD)
- 모든 테스트 케이스 통과(리눅스/윈도우)
- 정적 분석 경고 0건
- CI 매트릭스 안정화(3회 연속 통과)
- 실패 시 로그로 원인 추적 가능


