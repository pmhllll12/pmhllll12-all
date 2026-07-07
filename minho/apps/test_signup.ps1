#Requires -Version 5.1
param([switch]$StartServer)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Base = "http://127.0.0.1:8000"
$SignupUri = "$Base/signup"

function Test-PortOpen {
    param([int]$TimeoutMs = 2000)
    $c = $null
    try {
        $c = New-Object System.Net.Sockets.TcpClient
        $ar = $c.BeginConnect("127.0.0.1", 8000, $null, $null)
        if (-not $ar.AsyncWaitHandle.WaitOne($TimeoutMs, $false)) { return $false }
        $c.EndConnect($ar)
        return $true
    } catch { return $false }
    finally { if ($c) { try { $c.Close() } catch {} } }
}

if (-not (Test-PortOpen)) {
    Write-Host ""
    Write-Host "[연결 실패] API 서버가 127.0.0.1:8000 에서 실행 중이 아닙니다." -ForegroundColor Red
    Write-Host "Invoke-RestMethod 원격 서버 연결 불가 = 보통 이 경우입니다." -ForegroundColor DarkYellow
    Write-Host ""
    Write-Host "1) 다른 터미널에서:" -ForegroundColor Yellow
    Write-Host "   cd $Root"
    Write-Host "   python run_api.py"
    Write-Host "2) startup complete 후 다시: .\test_signup.ps1" -ForegroundColor Yellow
    Write-Host ""

    if ($StartServer) {
        Write-Host "[-StartServer] 새 창에서 API 실행..." -ForegroundColor Cyan
        Start-Process powershell -WorkingDirectory $Root -ArgumentList "-NoExit","-Command","cd `"$Root`"; python run_api.py"
        Write-Host "15초 대기..."
        $ok = $false
        for ($i = 0; $i -lt 30; $i++) {
            Start-Sleep -Milliseconds 500
            if (Test-PortOpen) { $ok = $true; break }
        }
        if (-not $ok) { Write-Host "포트가 안 열렸습니다. 새 창 오류 확인." -ForegroundColor Red; exit 1 }
        Write-Host "연결 OK" -ForegroundColor Green
    } else {
        Write-Host "자동 실행: .\test_signup.ps1 -StartServer" -ForegroundColor DarkGray
        exit 1
    }
}

$bodyJson = (@{ email = "a@b.com"; password = "secret12"; password_confirm = "secret12" } | ConvertTo-Json -Compress)
Write-Host ""
Write-Host "POST $SignupUri" -ForegroundColor Cyan
try {
    $r = Invoke-RestMethod -Uri $SignupUri -Method POST -ContentType "application/json; charset=utf-8" -Body $bodyJson
    $r | ConvertTo-Json
} catch {
    Write-Host "실패: $_" -ForegroundColor Red
    exit 1
}
