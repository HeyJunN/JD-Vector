# 🚀 Vercel 배포 빠른 시작 가이드

백엔드가 이미 배포되었으므로, 프론트엔드를 Vercel에 배포하는 과정입니다.

## 📋 사전 준비

백엔드 API URL: `https://jd-vector-api.fly.dev`

필요한 정보:
- [ ] Supabase URL
- [ ] Supabase Anon Key

---

## ⚡ 빠른 배포 (자동 스크립트)

PowerShell에서 실행:

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\JD-Vector\apps\web
.\deploy-vercel.ps1
```

스크립트가 다음을 자동으로 처리합니다:
1. ✅ Vercel CLI 설치 확인
2. ✅ Vercel 로그인
3. ✅ 빌드 테스트
4. ✅ 환경 변수 설정
5. ✅ 배포 실행

---

## 🔧 수동 배포

### 1단계: Vercel CLI 설치

```bash
npm install -g vercel
```

### 2단계: 로그인

```bash
vercel login
```

### 3단계: 배포

```bash
cd apps/web
vercel
```

질문에 다음과 같이 답변:
- Set up and deploy? → **Y**
- Link to existing project? → **N**
- Project name? → **jd-vector-web**
- Code directory? → **./** (기본값)
- Override settings? → **N**

### 4단계: 환경 변수 설정

**Vercel Dashboard 사용 (권장):**

1. https://vercel.com/dashboard 접속
2. `jd-vector-web` 프로젝트 선택
3. **Settings** > **Environment Variables**
4. 다음 변수 추가:

```
VITE_API_BASE_URL = https://jd-vector-api.fly.dev
VITE_SUPABASE_URL = https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY = your-anon-key
VITE_ENVIRONMENT = production
```

**또는 CLI 사용:**

```bash
vercel env add VITE_API_BASE_URL
# Value: https://jd-vector-api.fly.dev

vercel env add VITE_SUPABASE_URL
# Value: https://your-project.supabase.co

vercel env add VITE_SUPABASE_ANON_KEY
# Value: your-anon-key

vercel env add VITE_ENVIRONMENT
# Value: production
```

### 5단계: 환경 변수 적용을 위한 재배포

```bash
vercel --prod
```

---

## 🔗 백엔드 CORS 업데이트

배포 후 받은 Vercel URL을 백엔드 CORS에 추가하세요.

```bash
cd ../server

# Vercel 도메인을 CORS에 추가
flyctl secrets set ALLOWED_ORIGINS_CSV="http://localhost:3000,https://jd-vector-web.vercel.app,https://jd-vector-web-*.vercel.app"
```

---

## ✅ 배포 확인

### 1. 프론트엔드 동작 확인
- 브라우저에서 Vercel URL 열기
- 페이지 로딩 및 라우팅 확인
- 개발자 도구 > Console에서 에러 확인

### 2. 백엔드 연동 확인
- 개발자 도구 > Network 탭 열기
- API 요청이 `https://jd-vector-api.fly.dev`로 가는지 확인
- CORS 에러가 없는지 확인

### 3. 기능 테스트
- [ ] 파일 업로드 기능
- [ ] 분석 결과 표시
- [ ] 로드맵 생성

---

## 🐛 문제 해결

### CORS 에러

**증상:** `Access-Control-Allow-Origin` 에러

**해결:**
```bash
# 백엔드 CORS 설정 확인
cd ../server
flyctl secrets list

# Vercel 도메인이 포함되어 있는지 확인
flyctl secrets set ALLOWED_ORIGINS_CSV="...,https://your-vercel-url.vercel.app"
```

### 환경 변수가 undefined

**확인:**
- 환경 변수 이름이 `VITE_` 접두사로 시작하는지 확인
- Vercel Dashboard에서 환경 변수가 설정되었는지 확인
- 재배포 실행: `vercel --prod`

### 빌드 실패

```bash
# 로컬에서 빌드 테스트
npm run build

# node_modules 재설치
rm -rf node_modules
npm install
npm run build
```

---

## 📚 추가 자료

- [상세 배포 가이드](./DEPLOYMENT_VERCEL.md)
- [Vercel 문서](https://vercel.com/docs)
- [Vite 환경 변수](https://vitejs.dev/guide/env-and-mode.html)

---

## 🎉 완료!

배포가 완료되면 다음을 확인하세요:

✅ 프론트엔드: `https://jd-vector-web.vercel.app`
✅ 백엔드: `https://jd-vector-api.fly.dev`
✅ CORS 설정 완료
✅ 환경 변수 설정 완료

이제 JD-Vector 서비스가 운영 중입니다! 🚀
