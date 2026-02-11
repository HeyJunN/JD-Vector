# Fly.io CORS 설정 업데이트 스크립트 (PowerShell)
# 사용법: .\update-cors.ps1

Write-Host "🔧 JD-Vector CORS 설정 업데이트" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📝 참고사항:" -ForegroundColor Yellow
Write-Host "  - Vercel 도메인(*.vercel.app)은 자동으로 허용됩니다" -ForegroundColor Gray
Write-Host "  - localhost와 커스텀 도메인만 환경 변수에 추가하면 됩니다" -ForegroundColor Gray
Write-Host ""

# 기본 설정 제안
Write-Host "1️⃣ 권장 설정 사용 (localhost만 포함)" -ForegroundColor Cyan
Write-Host "   ALLOWED_ORIGINS_CSV=`"http://localhost:3000,http://localhost:5173`"" -ForegroundColor White
Write-Host ""
Write-Host "2️⃣ 커스텀 도메인 포함" -ForegroundColor Cyan
Write-Host "   ALLOWED_ORIGINS_CSV=`"http://localhost:3000,http://localhost:5173,https://yourdomain.com`"" -ForegroundColor White
Write-Host ""
Write-Host "3️⃣ 직접 입력" -ForegroundColor Cyan
Write-Host ""

Write-Host "선택 (1, 2, 또는 3): " -ForegroundColor Yellow -NoNewline
$choice = Read-Host

$corsValue = ""

switch ($choice) {
    "1" {
        $corsValue = "http://localhost:3000,http://localhost:5173"
        Write-Host "✅ 기본 설정을 사용합니다." -ForegroundColor Green
    }
    "2" {
        Write-Host "커스텀 도메인을 입력하세요 (예: https://yourdomain.com): " -ForegroundColor Yellow -NoNewline
        $customDomain = Read-Host
        if ($customDomain) {
            $corsValue = "http://localhost:3000,http://localhost:5173,$customDomain"
            Write-Host "✅ 커스텀 도메인이 추가되었습니다." -ForegroundColor Green
        } else {
            Write-Host "❌ 도메인이 입력되지 않았습니다. 기본 설정을 사용합니다." -ForegroundColor Yellow
            $corsValue = "http://localhost:3000,http://localhost:5173"
        }
    }
    "3" {
        Write-Host "ALLOWED_ORIGINS_CSV 값을 입력하세요 (쉼표로 구분): " -ForegroundColor Yellow -NoNewline
        $corsValue = Read-Host
    }
    default {
        Write-Host "❌ 잘못된 선택입니다. 기본 설정을 사용합니다." -ForegroundColor Red
        $corsValue = "http://localhost:3000,http://localhost:5173"
    }
}

Write-Host ""
Write-Host "📋 설정할 값:" -ForegroundColor Cyan
Write-Host "  ALLOWED_ORIGINS_CSV=`"$corsValue`"" -ForegroundColor White
Write-Host ""

Write-Host "이 설정을 Fly.io에 적용하시겠습니까? (Y/N): " -ForegroundColor Yellow -NoNewline
$confirm = Read-Host

if ($confirm -eq 'Y' -or $confirm -eq 'y') {
    Write-Host ""
    Write-Host "🚀 Fly.io secrets 업데이트 중..." -ForegroundColor Green

    flyctl secrets set "ALLOWED_ORIGINS_CSV=$corsValue"

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ CORS 설정이 성공적으로 업데이트되었습니다!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📊 변경사항:" -ForegroundColor Cyan
        Write-Host "  - localhost:3000, localhost:5173 (개발 환경)" -ForegroundColor White
        if ($corsValue -match "yourdomain|custom") {
            Write-Host "  - 커스텀 도메인 추가됨" -ForegroundColor White
        }
        Write-Host "  - 모든 *.vercel.app 도메인 (자동 허용)" -ForegroundColor White
        Write-Host ""
        Write-Host "⏱️ 앱이 자동으로 재시작됩니다 (약 30초 소요)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "🔍 다음 명령어로 확인하세요:" -ForegroundColor Cyan
        Write-Host "  flyctl logs" -ForegroundColor Gray
        Write-Host "  flyctl secrets list" -ForegroundColor Gray
    } else {
        Write-Host ""
        Write-Host "❌ 설정 업데이트에 실패했습니다." -ForegroundColor Red
        Write-Host "flyctl auth whoami 명령어로 로그인 상태를 확인해주세요." -ForegroundColor Gray
    }
} else {
    Write-Host "취소되었습니다." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "💡 추가 정보:" -ForegroundColor Cyan
Write-Host "  - CORS 설정 가이드: CORS_SETUP.md 참조" -ForegroundColor Gray
Write-Host "  - Vercel 도메인은 자동으로 허용되므로 별도 설정 불필요" -ForegroundColor Gray
