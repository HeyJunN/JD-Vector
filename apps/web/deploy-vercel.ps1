# JD-Vector 프론트엔드 Vercel 배포 스크립트 (PowerShell)
# 사용법: .\deploy-vercel.ps1

Write-Host "🚀 JD-Vector 프론트엔드 Vercel 배포 스크립트" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Vercel CLI 설치 확인
Write-Host "1️⃣ Vercel CLI 설치 확인 중..." -ForegroundColor Yellow
if (!(Get-Command vercel -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Vercel CLI가 설치되지 않았습니다." -ForegroundColor Red
    Write-Host "📥 Vercel CLI를 설치하시겠습니까? (Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "Vercel CLI 설치 중..." -ForegroundColor Green
        npm install -g vercel
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Vercel CLI 설치 실패. 배포를 중단합니다." -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ Vercel CLI가 설치되었습니다." -ForegroundColor Green
    } else {
        Write-Host "배포를 중단합니다." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Vercel CLI가 이미 설치되어 있습니다." -ForegroundColor Green
}
Write-Host ""

# 2. Vercel 로그인 확인
Write-Host "2️⃣ Vercel 로그인 확인 중..." -ForegroundColor Yellow
$loginCheck = vercel whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Vercel에 로그인되어 있지 않습니다." -ForegroundColor Red
    Write-Host "🔑 로그인을 진행합니다..." -ForegroundColor Yellow
    vercel login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 로그인 실패. 배포를 중단합니다." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Vercel에 로그인되어 있습니다: $loginCheck" -ForegroundColor Green
}
Write-Host ""

# 3. 프로덕션 빌드 테스트
Write-Host "3️⃣ 로컬 빌드 테스트를 진행하시겠습니까? (Y/N)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host "📦 빌드 중..." -ForegroundColor Green
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 빌드 실패. 에러를 확인해주세요." -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ 빌드가 성공했습니다." -ForegroundColor Green
} else {
    Write-Host "⚠️ 빌드 테스트를 건너뜁니다." -ForegroundColor Yellow
}
Write-Host ""

# 4. 환경 변수 확인 및 설정
Write-Host "4️⃣ 환경 변수 설정" -ForegroundColor Yellow
Write-Host "다음 환경 변수들이 Vercel에 설정되어 있어야 합니다:" -ForegroundColor Cyan
Write-Host "  - VITE_API_BASE_URL (https://jd-vector-api.fly.dev)" -ForegroundColor White
Write-Host "  - VITE_SUPABASE_URL" -ForegroundColor White
Write-Host "  - VITE_SUPABASE_ANON_KEY" -ForegroundColor White
Write-Host "  - VITE_ENVIRONMENT" -ForegroundColor White
Write-Host ""
Write-Host "환경 변수를 CLI로 설정하시겠습니까? (Y/N)" -ForegroundColor Yellow
Write-Host "(N 선택 시 Vercel Dashboard에서 수동으로 설정해야 합니다)" -ForegroundColor Gray
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "📝 환경 변수 입력:" -ForegroundColor Cyan

    Write-Host "VITE_API_BASE_URL (기본값: https://jd-vector-api.fly.dev):" -ForegroundColor White
    $apiUrl = Read-Host
    if ([string]::IsNullOrWhiteSpace($apiUrl)) {
        $apiUrl = "https://jd-vector-api.fly.dev"
    }

    Write-Host "VITE_SUPABASE_URL:" -ForegroundColor White
    $supabaseUrl = Read-Host

    Write-Host "VITE_SUPABASE_ANON_KEY:" -ForegroundColor White
    $supabaseAnonKey = Read-Host

    Write-Host ""
    Write-Host "환경 변수 설정 중..." -ForegroundColor Green

    # 환경 변수 설정
    if ($apiUrl) {
        Write-Host "VITE_API_BASE_URL" | vercel env add VITE_API_BASE_URL production
    }
    if ($supabaseUrl) {
        Write-Host "VITE_SUPABASE_URL" | vercel env add VITE_SUPABASE_URL production
    }
    if ($supabaseAnonKey) {
        Write-Host "VITE_SUPABASE_ANON_KEY" | vercel env add VITE_SUPABASE_ANON_KEY production
    }
    Write-Host "production" | vercel env add VITE_ENVIRONMENT production

    Write-Host "✅ 환경 변수가 설정되었습니다." -ForegroundColor Green
} else {
    Write-Host "⚠️ 환경 변수 설정을 건너뜁니다." -ForegroundColor Yellow
    Write-Host "Vercel Dashboard에서 수동으로 설정해주세요: https://vercel.com/dashboard" -ForegroundColor Gray
}
Write-Host ""

# 5. 배포 유형 선택
Write-Host "5️⃣ 배포 유형 선택" -ForegroundColor Yellow
Write-Host "1. 프로덕션 배포 (--prod)" -ForegroundColor Cyan
Write-Host "2. 프리뷰 배포 (테스트용)" -ForegroundColor Cyan
Write-Host "선택 (1 또는 2):" -ForegroundColor Yellow
$deployType = Read-Host

$prodFlag = ""
if ($deployType -eq "1") {
    $prodFlag = "--prod"
    Write-Host "✅ 프로덕션 배포를 진행합니다." -ForegroundColor Green
} else {
    Write-Host "✅ 프리뷰 배포를 진행합니다." -ForegroundColor Green
}
Write-Host ""

# 6. 배포 실행
Write-Host "6️⃣ 배포를 시작하시겠습니까? (Y/N)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host "🚀 배포 중..." -ForegroundColor Green
    Write-Host ""

    if ($prodFlag) {
        vercel $prodFlag
    } else {
        vercel
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ 배포가 완료되었습니다!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📊 다음 단계:" -ForegroundColor Cyan
        Write-Host "1. 배포된 URL을 브라우저에서 열어 확인하세요" -ForegroundColor White
        Write-Host "2. 백엔드 CORS 설정에 Vercel 도메인을 추가하세요:" -ForegroundColor White
        Write-Host "   cd ../server" -ForegroundColor Gray
        Write-Host "   flyctl secrets set ALLOWED_ORIGINS_CSV=`"...,https://your-app.vercel.app`"" -ForegroundColor Gray
        Write-Host ""
        Write-Host "🌐 유용한 명령어:" -ForegroundColor Cyan
        Write-Host "   - vercel ls (배포 목록)" -ForegroundColor White
        Write-Host "   - vercel logs (로그 확인)" -ForegroundColor White
        Write-Host "   - vercel inspect (상세 정보)" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "❌ 배포 실패. 로그를 확인해주세요." -ForegroundColor Red
        Write-Host "vercel logs 명령어로 로그를 확인할 수 있습니다." -ForegroundColor Gray
        exit 1
    }
} else {
    Write-Host "배포를 취소했습니다." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 배포 스크립트 실행을 종료합니다." -ForegroundColor Green