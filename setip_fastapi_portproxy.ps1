# setip_fastapi_portproxy.ps1
param(
  [int[]]$Ports = @(8000, 5601, 18081, 27017, 9200, 9300)
)
$ErrorActionPreference = "Stop"

# 1) WSL IP 탐지
$wslIp = wsl -e bash -lc "ip -4 addr show eth0 | sed -n 's/.*inet \([0-9.]*\)\/.*/\1/p'"
if ([string]::IsNullOrWhiteSpace($wslIp)) { throw "WSL IP 탐지 실패" }

# 2) IP Helper 서비스 기동(포트프록시 필요)
Start-Service iphlpsvc -ErrorAction SilentlyContinue

foreach ($Port in $Ports) {
    # 3) 방화벽 허용(없으면 생성)
    if (-not (Get-NetFirewallRule -DisplayName "FastAPI $Port" -ErrorAction SilentlyContinue)) {
        New-NetFirewallRule -DisplayName "FastAPI $Port" -Direction Inbound -Action Allow -Protocol TCP -LocalPort $Port | Out-Null
    }

    # 4) 기존 포트프록시 제거 후 재등록
    try { netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=$Port | Out-Null } catch {}
    netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=$Port connectaddress=$wslIp connectport=$Port | Out-Null

    # 5) 현 상태 출력
    Write-Host ("포워딩 설정: 0.0.0.0:{0} -> {1}:{0} (완료)" -f $Port, $wslIp)
}
netsh interface portproxy show v4tov4 | Out-Host
