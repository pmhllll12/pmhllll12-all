# 저장소 루트에서 실행: .\commit.ps1 "커밋 메시지"
# docs / backend / frontend 는 각각 별도 Git(서브모듈)입니다.
param(
    [Parameter(Position = 0)]
    [string]$Message = "update"
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Modules = @("backend", "frontend", "docs")

Write-Host "=== 서브모듈 커밋 (변경 있을 때만) ===" -ForegroundColor Cyan
foreach ($name in $Modules) {
    $path = Join-Path $Root $name
    Push-Location $path
    $status = git status --porcelain
    if ($status) {
        Write-Host "[$name] 변경 발견 → 커밋" -ForegroundColor Yellow
        git add -A
        git commit -m $Message
    }
    else {
        Write-Host "[$name] 변경 없음 (clean)" -ForegroundColor DarkGray
    }
    Pop-Location
}

Write-Host "`n=== 루트 저장소 (서브모듈 포인터) ===" -ForegroundColor Cyan
Push-Location $Root
git add backend frontend docs
$subStatus = git diff --cached --name-only
if ($subStatus) {
    git commit -m $Message
    Write-Host "루트 커밋 완료" -ForegroundColor Green
}
else {
    $other = git status --porcelain
    if ($other) {
        Write-Host "루트 기타 파일:" -ForegroundColor Yellow
        git status -sb
        Write-Host "필요 시: git add ... 후 git commit -m `"$Message`"" -ForegroundColor Yellow
    }
    else {
        Write-Host "루트도 커밋할 변경 없음" -ForegroundColor DarkGray
    }
}
git status -sb
Pop-Location

Write-Host "`n푸시: cd $Root; git push; 각 폴더에서 git push" -ForegroundColor Cyan
