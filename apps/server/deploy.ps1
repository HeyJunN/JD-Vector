# JD-Vector Backend 배포 스크립트 (PowerShell)
# 사용법: .\deploy.ps1

Write-Host "🚀 JD-Vector Backend 배포 스크립트" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# 1. Flyctl 설치 확인
Write-Host "1️⃣ Flyctl 설치 확인 중..." -ForegroundColor Yellow
if (!(Get-Command flyctl -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Flyctl이 설치되지 않았습니다." -ForegroundColor Red
    Write-Host "📥 Flyctl을 설치하시겠습니까? (Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "Flyctl 설치 중..." -ForegroundColor Green
        iwr https://fly.io/install.ps1 -useb | iex
        Write-Host "✅ Flyctl이 설치되었습니다. 터미널을 재시작한 후 다시 실행해주세요." -ForegroundColor Green
        exit 0
    } else {
        Write-Host "배포를 중단합니다." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Flyctl이 이미 설치되어 있습니다." -ForegroundColor Green
}
Write-Host ""

# 2. Fly.io 로그인 확인
Write-Host "2️⃣ Fly.io 로그인 확인 중..." -ForegroundColor Yellow
$loginCheck = flyctl auth whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Fly.io에 로그인되어 있지 않습니다." -ForegroundColor Red
    Write-Host "🔑 로그인을 진행합니다..." -ForegroundColor Yellow
    flyctl auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 로그인 실패. 배포를 중단합니다." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Fly.io에 로그인되어 있습니다." -ForegroundColor Green
}
Write-Host ""

# 3. Poetry 의존성 확인
Write-Host "3️⃣ Poetry 의존성 확인 중..." -ForegroundColor Yellow
if (!(Test-Path "poetry.lock")) {
    Write-Host "⚠️ poetry.lock 파일이 없습니다. 생성하시겠습니까? (Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq 'Y' -or $response -eq 'y') {
        poetry lock
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Poetry lock 생성 실패. 배포를 중단합니다." -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ poetry.lock이 생성되었습니다." -ForegroundColor Green
    }
} else {
    Write-Host "✅ poetry.lock 파일이 존재합니다." -ForegroundColor Green
}
Write-Host ""

# 4. 환경 변수 설정 안내
Write-Host "4️⃣ 환경 변수 설정 확인" -ForegroundColor Yellow
Write-Host "다음 환경 변수들이 Fly.io에 설정되어 있어야 합니다:" -ForegroundColor Cyan
Write-Host "  - OPENAI_API_KEY" -ForegroundColor White
Write-Host "  - SUPABASE_URL" -ForegroundColor White
Write-Host "  - SUPABASE_KEY" -ForegroundColor White
Write-Host "  - SUPABASE_ANON_KEY" -ForegroundColor White
Write-Host "  - DATABASE_URL" -ForegroundColor White
Write-Host "  - ALLOWED_ORIGINS_CSV" -ForegroundColor White
Write-Host ""
Write-Host "환경 변수를 설정하시겠습니까? (Y/N)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "📝 환경 변수 입력:" -ForegroundColor Cyan

    $openaiKey = Read-Host "OPENAI_API_KEY"
    $supabaseUrl = Read-Host "SUPABASE_URL"
    $supabaseKey = Read-Host "SUPABASE_KEY"
    $supabaseAnonKey = Read-Host "SUPABASE_ANON_KEY"
    $databaseUrl = Read-Host "DATABASE_URL"
    $allowedOrigins = Read-Host "ALLOWED_ORIGINS_CSV (쉼표로 구분)"

    Write-Host ""
    Write-Host "환경 변수 설정 중..." -ForegroundColor Green

    if ($openaiKey) { flyctl secrets set "OPENAI_API_KEY=$openaiKey" }
    if ($supabaseUrl) { flyctl secrets set "SUPABASE_URL=$supabaseUrl" }
    if ($supabaseKey) { flyctl secrets set "SUPABASE_KEY=$supabaseKey" }
    if ($supabaseAnonKey) { flyctl secrets set "SUPABASE_ANON_KEY=$supabaseAnonKey" }
    if ($databaseUrl) { flyctl secrets set "DATABASE_URL=$databaseUrl" }
    if ($allowedOrigins) { flyctl secrets set "ALLOWED_ORIGINS_CSV=$allowedOrigins" }

    Write-Host "✅ 환경 변수가 설정되었습니다." -ForegroundColor Green
} else {
    Write-Host "⚠️ 환경 변수 설정을 건너뜁니다. 수동으로 설정해주세요." -ForegroundColor Yellow
}
Write-Host ""

# 5. 배포
Write-Host "5️⃣ 배포를 시작하시겠습니까? (Y/N)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host "🚀 배포 중..." -ForegroundColor Green
    flyctl deploy

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ 배포가 완료되었습니다!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📊 배포 상태 확인:" -ForegroundColor Cyan
        flyctl status
        Write-Host ""
        Write-Host "🌐 앱 열기: flyctl open" -ForegroundColor Cyan
        Write-Host "📝 로그 확인: flyctl logs" -ForegroundColor Cyan
    } else {
        Write-Host "❌ 배포 실패. 로그를 확인해주세요." -ForegroundColor Red
        flyctl logs --tail 100
        exit 1
    }
} else {
    Write-Host "배포를 취소했습니다." -ForegroundColor Yellow
}
