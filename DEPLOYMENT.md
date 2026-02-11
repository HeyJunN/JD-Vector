# JD-Vector 전체 배포 가이드

이 문서는 JD-Vector 프로젝트의 백엔드(FastAPI)와 프론트엔드(React)를 배포하는 전체 과정을 설명합니다.

## 📐 아키텍처

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Frontend      │─────>│    Backend       │─────>│   Supabase      │
│   (Vercel)      │ CORS │   (Fly.io)       │      │   (Database)    │
│                 │      │                  │      │                 │
│ React + Vite    │      │ FastAPI + Python │      │ PostgreSQL      │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

**배포 플랫폼:**
- 🚀 **백엔드:** Fly.io (`https://jd-vector-api.fly.dev`)
- 🌐 **프론트엔드:** Vercel (`https://jd-vector-web.vercel.app`)
- 💾 **데이터베이스:** Supabase (PostgreSQL + Vector Store)

---

## ✅ 배포 상태

### 백엔드 (Fly.io)
- [x] Dockerfile 생성
- [x] fly.toml 설정
- [x] 환경 변수 설정
- [x] 배포 완료
- [x] 헬스체크 통과

**URL:** https://jd-vector-api.fly.dev

### 프론트엔드 (Vercel)
- [x] vercel.json 생성
- [x] 환경 변수 템플릿
- [x] 배포 스크립트 준비
- [ ] 배포 실행 필요
- [ ] CORS 업데이트 필요

**배포 예정 URL:** https://jd-vector-web.vercel.app

---

## 🚀 빠른 시작

### 1️⃣ 백엔드 배포 (완료)

```powershell
cd apps/server
.\deploy.ps1
```

**상세 가이드:** [apps/server/DEPLOYMENT.md](./apps/server/DEPLOYMENT.md)

### 2️⃣ 프론트엔드 배포 (다음 단계)

```powershell
cd apps/web
.\deploy-vercel.ps1
```

**빠른 시작:** [apps/web/QUICKSTART.md](./apps/web/QUICKSTART.md)
**상세 가이드:** [apps/web/DEPLOYMENT_VERCEL.md](./apps/web/DEPLOYMENT_VERCEL.md)

### 3️⃣ CORS 업데이트

프론트엔드 배포 후:

```bash
cd apps/server
flyctl secrets set ALLOWED_ORIGINS_CSV="http://localhost:3000,https://jd-vector-web.vercel.app,https://jd-vector-web-*.vercel.app"
```

---

## 🔧 환경 변수 설정

### 백엔드 (Fly.io)

```bash
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-key
SUPABASE_ANON_KEY=your-anon-key
DATABASE_URL=postgresql://...
ALLOWED_ORIGINS_CSV=http://localhost:3000,https://jd-vector-web.vercel.app
```

**설정 방법:**
```bash
cd apps/server
flyctl secrets set KEY=value
```

### 프론트엔드 (Vercel)

```bash
VITE_API_BASE_URL=https://jd-vector-api.fly.dev
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_ENVIRONMENT=production
```

**설정 방법:**
1. https://vercel.com/dashboard 접속
2. 프로젝트 > Settings > Environment Variables
3. 변수 추가

또는 CLI:
```bash
cd apps/web
vercel env add VITE_API_BASE_URL
```

---

## 📝 배포 체크리스트

### 배포 전 준비
- [ ] Fly.io 계정 생성
- [ ] Vercel 계정 생성
- [ ] Supabase 프로젝트 생성
- [ ] OpenAI API Key 발급
- [ ] 모든 환경 변수 준비

### 백엔드 배포
- [x] Flyctl 설치
- [x] Dockerfile 생성
- [x] fly.toml 설정
- [x] Poetry 의존성 확인
- [x] 환경 변수 설정
- [x] 배포 실행
- [x] 헬스체크 확인 (`/health`)
- [x] API 문서 확인 (`/docs`)

### 프론트엔드 배포
- [x] Vercel CLI 설치 준비
- [x] vercel.json 생성
- [x] 환경 변수 템플릿 준비
- [ ] 로컬 빌드 테스트 (`npm run build`)
- [ ] Vercel 배포 실행
- [ ] 환경 변수 설정
- [ ] 배포 확인

### 연동 확인
- [ ] 프론트엔드에서 백엔드 API 호출
- [ ] CORS 설정 확인
- [ ] 파일 업로드 기능 테스트
- [ ] 분석 기능 테스트
- [ ] 로드맵 생성 테스트

---

## 🔍 배포 확인 방법

### 백엔드 헬스체크

```bash
# cURL
curl https://jd-vector-api.fly.dev/health

# 브라우저
https://jd-vector-api.fly.dev/docs
```

**예상 응답:**
```json
{
  "status": "ok"
}
```

### 프론트엔드 확인

1. 브라우저에서 Vercel URL 접속
2. 개발자 도구 > Console 열기
3. Network 탭에서 API 요청 확인
4. CORS 에러가 없는지 확인

### CORS 테스트

```javascript
// 브라우저 Console에서
fetch('https://jd-vector-api.fly.dev/health')
  .then(res => res.json())
  .then(data => console.log('✅ CORS OK:', data))
  .catch(err => console.error('❌ CORS Error:', err))
```

---

## 🛠️ 유용한 명령어

### 백엔드 (Fly.io)

```bash
# 로그 확인
flyctl logs

# 앱 상태
flyctl status

# 환경 변수 목록
flyctl secrets list

# SSH 접속
flyctl ssh console

# 재배포
flyctl deploy
```

### 프론트엔드 (Vercel)

```bash
# 배포 목록
vercel ls

# 로그 확인
vercel logs

# 환경 변수 목록
vercel env ls

# 프로덕션 배포
vercel --prod
```

---

## 🐛 트러블슈팅

### CORS 에러

**문제:** `Access-Control-Allow-Origin` 에러

**해결:**
```bash
# 1. 백엔드 CORS 설정 확인
cd apps/server
flyctl secrets list

# 2. Vercel 도메인 추가
flyctl secrets set ALLOWED_ORIGINS_CSV="...,https://your-vercel-domain.vercel.app"

# 3. 백엔드 재시작 (자동)
```

### 환경 변수 문제

**백엔드:**
```bash
# 확인
flyctl secrets list

# 재설정
flyctl secrets set KEY=new-value
```

**프론트엔드:**
- Vite는 `VITE_` 접두사가 있는 변수만 노출
- 환경 변수 변경 후 재배포 필요

### 빌드 실패

**백엔드:**
```bash
# 로컬 Docker 테스트
cd apps/server
docker build -t jd-vector-api .
docker run -p 8080:8080 --env-file .env jd-vector-api
```

**프론트엔드:**
```bash
# 로컬 빌드 테스트
cd apps/web
npm run build
npm run preview
```

---

## 📊 모니터링

### Fly.io (백엔드)

```bash
# 메트릭 확인
flyctl metrics

# 리소스 사용량
flyctl status
```

### Vercel (프론트엔드)

- **Analytics:** https://vercel.com/dashboard/analytics
- **Logs:** https://vercel.com/dashboard/logs
- **Deployments:** https://vercel.com/dashboard/deployments

---

## 💰 비용 최적화

### Fly.io 무료 티어
- ✅ 3개의 작은 VM (256MB RAM)
- ✅ Auto-stop/start 설정으로 비용 절감
- ✅ 현재 설정: `min_machines_running = 0`

### Vercel 무료 티어
- ✅ 개인 프로젝트 무제한
- ✅ 100GB 대역폭/월
- ✅ 자동 HTTPS 및 CDN

---

## 🔐 보안 체크리스트

- [ ] 환경 변수에 민감한 정보 저장 (코드에 하드코딩 금지)
- [ ] CORS 설정을 특정 도메인으로 제한
- [ ] HTTPS 강제 사용
- [ ] API Rate Limiting 고려
- [ ] Supabase RLS (Row Level Security) 설정
- [ ] 정기적인 의존성 업데이트

---

## 📚 참고 자료

### 공식 문서
- [Fly.io Docs](https://fly.io/docs/)
- [Vercel Docs](https://vercel.com/docs)
- [Supabase Docs](https://supabase.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Vite Docs](https://vitejs.dev/)

### 프로젝트 가이드
- [백엔드 배포 가이드](./apps/server/DEPLOYMENT.md)
- [프론트엔드 배포 가이드](./apps/web/DEPLOYMENT_VERCEL.md)
- [프론트엔드 빠른 시작](./apps/web/QUICKSTART.md)

---

## 🎯 다음 단계

### 배포 후 개선사항
1. **커스텀 도메인** 설정
2. **CI/CD 파이프라인** 구축 (GitHub Actions)
3. **모니터링 및 알림** 설정
4. **성능 최적화** (Lighthouse 점수 개선)
5. **에러 트래킹** (Sentry 연동)
6. **백업 전략** 수립

### 추가 기능
- [ ] 사용자 인증 (Supabase Auth)
- [ ] 이메일 알림
- [ ] PDF 리포트 생성
- [ ] 다국어 지원
- [ ] 다크 모드

---

## 💡 팁

1. **환경 변수는 .env 파일에 저장하지 말고** Fly.io Secrets와 Vercel Environment Variables 사용
2. **로컬 개발 시** `.env.local` 파일 사용 (Git에 커밋하지 않음)
3. **배포 전 항상 로컬 빌드 테스트** 실행
4. **프로덕션 배포 전 Preview 배포**로 먼저 테스트
5. **CORS 설정은 구체적인 도메인**으로 제한 (와일드카드 최소화)

---

## ✨ 완료!

배포가 모두 완료되면:

✅ **백엔드:** https://jd-vector-api.fly.dev
✅ **프론트엔드:** https://jd-vector-web.vercel.app
✅ **API 문서:** https://jd-vector-api.fly.dev/docs

이제 JD-Vector가 실제 서비스로 운영됩니다! 🎉

**문제가 발생하면:**
- 로그 확인: `flyctl logs` / `vercel logs`
- 이슈 등록: GitHub Issues
- 문서 재확인: 각 서비스의 배포 가이드
