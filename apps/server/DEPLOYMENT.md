# JD-Vector Backend 배포 가이드 (Fly.io)

이 가이드는 FastAPI 백엔드를 Fly.io에 배포하는 전체 과정을 설명합니다.

## 사전 준비

### 1. 필수 도구 설치

#### Windows에서 Flyctl 설치

**PowerShell (관리자 권한):**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**설치 확인:**
```bash
flyctl version
```

#### Vercel CLI 설치 (프론트엔드 배포용)

```bash
npm install -g vercel
```

### 2. Fly.io 계정 설정

**회원가입 및 로그인:**
```bash
flyctl auth signup
# 또는 기존 계정이 있다면
flyctl auth login
```

**신용카드 등록** (무료 티어 사용에도 필요):
```bash
flyctl auth billing
```

---

## 배포 프로세스

### 1단계: 의존성 Lock 파일 생성

```bash
cd apps/server
poetry lock
```

### 2단계: Fly.io 앱 생성

```bash
# apps/server 디렉토리에서 실행
flyctl apps create jd-vector-api
```

**참고:** 앱 이름이 이미 사용 중이라면 다른 이름을 선택하고 `fly.toml`의 `app` 필드를 업데이트하세요.

### 3단계: 환경 변수(Secrets) 설정

배포 전에 필수 환경 변수를 Fly.io에 설정해야 합니다:

```bash
# OpenAI API Key
flyctl secrets set OPENAI_API_KEY="your-openai-api-key"

# Supabase 설정
flyctl secrets set SUPABASE_URL="your-supabase-url"
flyctl secrets set SUPABASE_KEY="your-supabase-service-key"
flyctl secrets set SUPABASE_ANON_KEY="your-supabase-anon-key"

# Database URL (Supabase PostgreSQL)
flyctl secrets set DATABASE_URL="postgresql://user:password@host:port/database"

# CORS Origins (배포 후 Vercel 도메인 추가)
flyctl secrets set ALLOWED_ORIGINS_CSV="http://localhost:3000,https://your-app.vercel.app"
```

**환경 변수 확인:**
```bash
flyctl secrets list
```

### 4단계: 첫 배포

```bash
flyctl deploy
```

이 명령어는:
1. Dockerfile을 기반으로 이미지 빌드
2. Fly.io에 이미지 업로드
3. 앱 실행 및 헬스체크

**배포 진행 상황 모니터링:**
```bash
flyctl logs
```

### 5단계: 배포 확인

```bash
# 앱 상태 확인
flyctl status

# 앱 URL 열기
flyctl open

# 헬스체크 확인
flyctl open /health
```

**API 엔드포인트:**
- 메인: `https://jd-vector-api.fly.dev/`
- 헬스체크: `https://jd-vector-api.fly.dev/health`
- API 문서: `https://jd-vector-api.fly.dev/docs`

---

## 업데이트 배포

코드 변경 후 재배포:

```bash
# apps/server 디렉토리에서
flyctl deploy
```

---

## CORS 설정 업데이트 (Vercel 배포 후)

프론트엔드를 Vercel에 배포한 후, 백엔드 CORS 설정을 업데이트해야 합니다:

```bash
# Vercel 도메인을 CORS 허용 목록에 추가
flyctl secrets set ALLOWED_ORIGINS_CSV="http://localhost:3000,https://your-app.vercel.app,https://your-app-*.vercel.app"
```

**자동 재시작:** Secrets 변경 시 앱이 자동으로 재시작됩니다.

---

## 유용한 명령어

### 로그 확인
```bash
# 실시간 로그
flyctl logs

# 최근 로그
flyctl logs --tail 100
```

### 앱 스케일링
```bash
# 메모리 증가
flyctl scale memory 1024

# VM 개수 조정
flyctl scale count 2
```

### SSH 접속
```bash
flyctl ssh console
```

### 앱 일시 중지/재개
```bash
# 일시 중지
flyctl apps pause

# 재개
flyctl apps resume
```

### 앱 삭제
```bash
flyctl apps destroy jd-vector-api
```

---

## 트러블슈팅

### 1. 빌드 실패 시

**Poetry lock 파일 재생성:**
```bash
poetry lock --no-update
```

**Docker 로컬 테스트:**
```bash
docker build -t jd-vector-api .
docker run -p 8080:8080 --env-file .env jd-vector-api
```

### 2. 헬스체크 실패 시

**로그 확인:**
```bash
flyctl logs --tail 200
```

**헬스체크 엔드포인트 테스트:**
```bash
curl https://jd-vector-api.fly.dev/health
```

### 3. 환경 변수 문제

**Secrets 확인:**
```bash
flyctl secrets list
```

**특정 Secret 삭제:**
```bash
flyctl secrets unset VARIABLE_NAME
```

### 4. CORS 오류

**현재 설정 확인:**
```bash
flyctl ssh console -C "env | grep ALLOWED_ORIGINS"
```

**재설정:**
```bash
flyctl secrets set ALLOWED_ORIGINS_CSV="https://your-domain.com"
```

---

## 비용 최적화

Fly.io 무료 티어:
- **무료 할당량:** 3개의 작은 VM (256MB RAM)
- **Auto-stop:** 트래픽이 없을 때 자동으로 중지
- **Auto-start:** 요청이 들어오면 자동으로 시작

현재 설정(`fly.toml`):
- `auto_stop_machines = true`
- `auto_start_machines = true`
- `min_machines_running = 0`

이 설정으로 사용하지 않을 때 비용이 발생하지 않습니다.

---

## 다음 단계: 프론트엔드 배포

백엔드 배포가 완료되면:

1. Vercel에 프론트엔드 배포
2. Vercel 도메인을 백엔드 CORS에 추가
3. 프론트엔드 환경 변수에 백엔드 API URL 설정

**프론트엔드 환경 변수:**
```env
VITE_API_URL=https://jd-vector-api.fly.dev
```

---

## 참고 자료

- [Fly.io Documentation](https://fly.io/docs/)
- [Fly.io Python Guide](https://fly.io/docs/languages-and-frameworks/python/)
- [Fly.io Pricing](https://fly.io/docs/about/pricing/)
