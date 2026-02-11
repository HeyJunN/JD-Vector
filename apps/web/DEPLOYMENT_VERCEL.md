# JD-Vector 프론트엔드 배포 가이드 (Vercel)

이 가이드는 React + Vite 프론트엔드를 Vercel에 배포하는 전체 과정을 설명합니다.

## 사전 준비

### 1. Vercel CLI 설치

**npm으로 전역 설치:**
```bash
npm install -g vercel
```

**설치 확인:**
```bash
vercel --version
```

### 2. Vercel 계정 설정

**로그인:**
```bash
vercel login
```

브라우저가 열리면 GitHub, GitLab, 또는 이메일로 로그인하세요.

---

## 배포 프로세스

### 방법 1: Vercel CLI로 직접 배포 (빠른 배포)

#### 1️⃣ 프로젝트 디렉토리로 이동

```bash
cd C:\Users\ASUS\OneDrive\Desktop\JD-Vector\apps\web
```

#### 2️⃣ 첫 배포 (초기 설정)

```bash
vercel
```

다음 질문들에 대답하세요:

```
? Set up and deploy "~/JD-Vector/apps/web"? [Y/n] Y
? Which scope do you want to deploy to? [Your Account]
? Link to existing project? [y/N] N
? What's your project's name? jd-vector-web
? In which directory is your code located? ./
? Want to override the settings? [y/N] N
```

**자동 감지되는 설정:**
- **Build Command:** `npm run build` (package.json에서 자동 감지)
- **Output Directory:** `dist` (vercel.json에서 설정됨)
- **Framework:** Vite

#### 3️⃣ 환경 변수 설정

배포가 완료되면 환경 변수를 설정해야 합니다:

```bash
# 프로덕션 백엔드 URL
vercel env add VITE_API_BASE_URL

# 입력 프롬프트에서 값 입력
# Value: https://jd-vector-api.fly.dev
# Environments: Production, Preview, Development 모두 선택

# Supabase URL
vercel env add VITE_SUPABASE_URL
# Value: https://your-project.supabase.co

# Supabase Anon Key
vercel env add VITE_SUPABASE_ANON_KEY
# Value: your-supabase-anon-key

# 환경 설정
vercel env add VITE_ENVIRONMENT
# Value: production
```

**환경 변수 일괄 설정 (편리한 방법):**

Vercel Dashboard를 사용하세요:
1. https://vercel.com/dashboard 접속
2. 프로젝트 선택 (jd-vector-web)
3. **Settings** > **Environment Variables** 이동
4. 다음 변수들을 추가:

| Key | Value | Environments |
|-----|-------|--------------|
| `VITE_API_BASE_URL` | `https://jd-vector-api.fly.dev` | Production, Preview, Development |
| `VITE_SUPABASE_URL` | `https://your-project.supabase.co` | Production, Preview, Development |
| `VITE_SUPABASE_ANON_KEY` | `your-supabase-anon-key` | Production, Preview, Development |
| `VITE_ENVIRONMENT` | `production` | Production |
| `VITE_ENVIRONMENT` | `development` | Preview, Development |

#### 4️⃣ 환경 변수 적용을 위한 재배포

환경 변수를 설정한 후 재배포해야 적용됩니다:

```bash
# 프로덕션 배포
vercel --prod
```

#### 5️⃣ 배포 확인

배포가 완료되면 터미널에 URL이 표시됩니다:
- **Production:** `https://jd-vector-web.vercel.app`
- **Preview:** `https://jd-vector-web-{hash}.vercel.app`

브라우저에서 열어서 확인:
```bash
vercel open
```

---

### 방법 2: GitHub 연동 자동 배포 (권장)

#### 1️⃣ GitHub에 코드 푸시

```bash
cd C:\Users\ASUS\OneDrive\Desktop\JD-Vector

# 변경사항 커밋
git add .
git commit -m "feat: add Vercel deployment configuration"
git push origin main
```

#### 2️⃣ Vercel에서 GitHub 프로젝트 연동

1. https://vercel.com/new 접속
2. **Import Git Repository** 선택
3. GitHub 저장소 선택: `your-username/JD-Vector`
4. **Configure Project** 설정:
   - **Framework Preset:** Vite
   - **Root Directory:** `apps/web`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

5. **Environment Variables** 추가:
   ```
   VITE_API_BASE_URL=https://jd-vector-api.fly.dev
   VITE_SUPABASE_URL=https://your-project.supabase.co
   VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
   VITE_ENVIRONMENT=production
   ```

6. **Deploy** 클릭

**자동 배포 설정:**
- `main` 브랜치 푸시 → 자동으로 프로덕션 배포
- Pull Request 생성 → 자동으로 Preview 배포

---

## 백엔드 CORS 업데이트

프론트엔드가 배포되면 백엔드 CORS 설정을 업데이트해야 합니다.

### Vercel 도메인 확인

배포 후 받은 도메인 예시:
- `https://jd-vector-web.vercel.app`
- `https://jd-vector-web-*.vercel.app` (Preview 배포용)

### Fly.io 백엔드에 CORS 추가

```bash
cd C:\Users\ASUS\OneDrive\Desktop\JD-Vector\apps\server

# CORS 허용 도메인 업데이트
flyctl secrets set ALLOWED_ORIGINS_CSV="http://localhost:3000,https://jd-vector-web.vercel.app,https://jd-vector-web-*.vercel.app"
```

**참고:** `*` 와일드카드는 Preview 배포 URL을 위한 것입니다.

---

## 유용한 명령어

### 배포 관리

```bash
# 프로덕션 배포
vercel --prod

# 프리뷰 배포 (테스트용)
vercel

# 배포 목록 확인
vercel ls

# 최신 배포 로그 확인
vercel logs
```

### 환경 변수 관리

```bash
# 환경 변수 목록 확인
vercel env ls

# 환경 변수 추가
vercel env add VARIABLE_NAME

# 환경 변수 제거
vercel env rm VARIABLE_NAME

# 특정 환경의 변수 가져오기
vercel env pull .env.production
```

### 프로젝트 관리

```bash
# 프로젝트 정보 확인
vercel inspect

# 프로젝트 삭제
vercel remove jd-vector-web

# 도메인 추가
vercel domains add yourdomain.com

# 도메인 목록
vercel domains ls
```

---

## 빌드 최적화

### 1. Vite 빌드 최적화 (이미 적용됨)

`vite.config.ts`에 다음 설정이 적용되어 있습니다:

```typescript
build: {
  outDir: 'dist',
  sourcemap: true,
}
```

### 2. 프로덕션 빌드 테스트 (로컬)

배포 전에 로컬에서 프로덕션 빌드를 테스트하세요:

```bash
# 빌드
npm run build

# 프리뷰
npm run preview
```

브라우저에서 `http://localhost:4173` 접속하여 확인

### 3. Bundle 크기 분석

큰 번들을 최적화하려면:

```bash
# vite-plugin-visualizer 설치
npm install -D rollup-plugin-visualizer

# vite.config.ts에 추가
import { visualizer } from 'rollup-plugin-visualizer';

plugins: [
  react(),
  tsconfigPaths(),
  visualizer({ open: true })
]

# 빌드 후 자동으로 번들 분석 리포트 열림
npm run build
```

---

## 트러블슈팅

### 1. 빌드 실패 시

**에러: "Cannot find module"**
```bash
# node_modules 재설치
rm -rf node_modules package-lock.json
npm install
```

**TypeScript 에러:**
```bash
# 타입 체크
npm run build
```

### 2. 환경 변수가 적용되지 않음

Vite는 `VITE_` 접두사가 있는 환경 변수만 클라이언트에 노출합니다.

**확인 사항:**
- ✅ `VITE_API_BASE_URL` (올바름)
- ❌ `API_BASE_URL` (잘못됨 - VITE_ 접두사 없음)

**재배포 필요:**
환경 변수를 변경한 후에는 재배포해야 적용됩니다:
```bash
vercel --prod
```

### 3. CORS 에러

**증상:** 프론트엔드에서 백엔드 API 호출 시 CORS 에러

**해결:**
1. 백엔드 로그 확인:
   ```bash
   flyctl logs
   ```

2. CORS 설정 확인:
   ```bash
   flyctl secrets list
   ```

3. Vercel 도메인이 CORS에 포함되어 있는지 확인:
   ```bash
   flyctl secrets set ALLOWED_ORIGINS_CSV="...,https://your-vercel-domain.vercel.app"
   ```

### 4. 라우팅 404 에러

**증상:** `/about` 같은 경로에서 새로고침 시 404 에러

**해결:** `vercel.json`의 `rewrites` 설정이 올바른지 확인
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

### 5. 환경별 설정 분리

**개발/프로덕션 환경 분리:**

`.env.development` (로컬 개발):
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENVIRONMENT=development
```

`.env.production` (Vercel에서 설정):
```env
VITE_API_BASE_URL=https://jd-vector-api.fly.dev
VITE_ENVIRONMENT=production
```

---

## 성능 최적화 체크리스트

- [x] **vercel.json** 설정 완료
- [x] **Static Asset Caching** 설정됨 (31536000초 = 1년)
- [x] **SPA Routing** 리라이트 규칙 적용
- [ ] **이미지 최적화** - Vercel Image Optimization 사용 고려
- [ ] **폰트 최적화** - 로컬 폰트 사용 또는 CDN 최적화
- [ ] **Code Splitting** - React.lazy() 및 Suspense 사용
- [ ] **Bundle 크기 분석** - 불필요한 의존성 제거

---

## 배포 후 확인 사항

### 1. 프론트엔드 동작 확인
- [ ] 메인 페이지 로딩
- [ ] 라우팅 동작 (페이지 전환)
- [ ] API 연동 테스트 (백엔드 호출)
- [ ] 파일 업로드 기능
- [ ] Supabase 연동

### 2. 백엔드 연동 확인
```bash
# 브라우저 개발자 도구 > Network 탭에서
# API 요청이 https://jd-vector-api.fly.dev로 가는지 확인
```

### 3. 성능 확인
- **Lighthouse** 점수 확인 (Chrome DevTools)
- **Core Web Vitals** 확인
- **Bundle 크기** 확인

---

## 다음 단계

### 커스텀 도메인 설정 (선택사항)

1. **도메인 추가:**
   ```bash
   vercel domains add yourdomain.com
   ```

2. **DNS 설정:**
   도메인 등록 업체에서 다음 레코드 추가:
   ```
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   ```

3. **자동 HTTPS:**
   Vercel이 자동으로 SSL 인증서를 발급합니다.

### 모니터링 및 분석

- **Vercel Analytics** 활성화 (프로젝트 설정에서)
- **Vercel Speed Insights** 활성화
- **Sentry** 또는 다른 에러 트래킹 도구 연동

---

## 참고 자료

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel CLI Reference](https://vercel.com/docs/cli)
- [Vite on Vercel](https://vercel.com/docs/frameworks/vite)
- [Environment Variables](https://vercel.com/docs/environment-variables)
