# JD-Vector

**AI 기반 직무 적합도 분석 및 맞춤형 커리어 로드맵 서비스**

RAG(Retrieval-Augmented Generation) 파이프라인을 활용하여 채용 공고(JD)와 지원자 이력서 간의 스킬 갭을 정밀 분석하고, 개인화된 8주 학습 커리큘럼을 자동 생성합니다.

## 프로젝트 개요

### 🎯 핵심 가치
- **데이터 정합성**: Vector DB와 연동된 `document_id` 기반 아키텍처로 파일-벡터 간 일관성 보장
- **AI 기반 분석**: GPT-4o mini와 임베딩 모델을 활용한 섹션별 역량 매칭 및 피드백 생성
- **실행 가능한 로드맵**: 부족 역량 70% 이상 집중 학습 + 80개 이상의 큐레이션된 한국어 리소스 제공

### 🛠️ 기술 스택

#### Frontend
- **Framework**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS (Glassmorphism + Slate-950 기반 다크 테마)
- **UI Components**: Lucide React (아이콘), Recharts (데이터 시각화), Framer Motion (애니메이션)
- **HTTP Client**: Axios (타임아웃 최적화: 120초)
- **State Management**: React Hooks (로컬 상태)

#### Backend
- **Framework**: FastAPI (Python 3.11) + Uvicorn (ASGI 서버)
- **Dependency Management**: Poetry
- **AI/LLM**: LangChain + OpenAI (GPT-4o mini, text-embedding-3-small)
- **Vector Database**: Supabase (PostgreSQL + pgvector)
- **Utilities**: tenacity (재시도 로직), tiktoken (토큰 계산), PyPDFLoader (PDF 파싱)

#### Infrastructure
- **배포**:
  - Frontend: Vercel (https://web-kostiszxr-heyjunns-projects.vercel.app)
  - Backend: Fly.io (https://jd-vector-api.fly.dev)
- **데이터베이스**: Supabase (Vector Store + 파일 메타데이터)
- **CORS**: SmartCORSMiddleware (Vercel 도메인 자동 인식)
- **컨테이너화**: Docker (Multi-stage build with Poetry)
- **CI/CD**: GitHub Actions (예정)

## 프로젝트 구조

```
jd-vector/
├── apps/
│   ├── web/          # Frontend (React + Vite + TypeScript)
│   └── server/       # Backend (FastAPI + LangChain)
├── packages/
│   ├── shared-types/ # 공통 TypeScript 타입
│   └── config/       # 공통 설정
├── data-lab/         # 데이터 분석 실험
├── docs/             # 문서
└── scripts/          # 유틸리티 스크립트
```

## 🚀 배포된 서비스

### 프로덕션 URL
- **Frontend**: https://web-kostiszxr-heyjunns-projects.vercel.app
- **Backend API**: https://jd-vector-api.fly.dev
- **API 문서**: https://jd-vector-api.fly.dev/docs

### 배포 가이드
- [전체 배포 가이드](./DEPLOYMENT.md) - 백엔드 + 프론트엔드 배포 프로세스
- [백엔드 배포 (Fly.io)](./apps/server/DEPLOYMENT.md)
- [프론트엔드 배포 (Vercel)](./apps/web/DEPLOYMENT_VERCEL.md)
- [프론트엔드 빠른 시작](./apps/web/QUICKSTART.md)
- [CORS 설정 가이드](./apps/server/CORS_SETUP.md)

---

## 시작하기

### 사전 요구사항

- Node.js >= 20.0.0
- pnpm >= 8.0.0
- Python >= 3.11
- Poetry (Python 패키지 관리)

### 1. Node.js 버전 설정

```bash
nvm use
```

### 2. Frontend 설정

```bash
cd apps/web
pnpm install
cp .env.example .env
# .env 파일을 편집하여 환경 변수 설정
```

### 3. Backend 설정

```bash
cd apps/server
poetry install
cp .env.example .env
# .env 파일을 편집하여 API 키 등 설정
```

### 4. 환경 변수 설정

#### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

#### Backend (.env)

```env
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/jd_vector
```

### 5. 개발 서버 실행

#### Frontend

```bash
pnpm dev
# http://localhost:3000에서 실행
```

#### Backend

```bash
pnpm dev:server
# http://localhost:8000에서 실행
# API 문서: http://localhost:8000/docs
```

## 핵심 기능

### 1. 🔄 Document ID 기반 RAG 파이프라인

**데이터 정합성 보장:**
- 단순 `file_id`가 아닌 **Vector DB 연동 `document_id`** 사용
- Supabase pgvector와 완벽한 동기화로 데이터 불일치 방지
- API 422 에러 원천 차단 (파일-벡터 매핑 무결성)

**자동 벡터화:**
- PDF 업로드 시 BackgroundTasks를 통한 자동 임베딩 생성
- OpenAI text-embedding-3-small (1536차원) 활용
- tenacity 기반 재시도 로직으로 안정성 확보

### 2. 🎯 섹션별 스킬 갭 분석

**정밀 매칭 알고리즘:**
- 이력서와 JD를 섹션별로 분류 (기술 스택, 경험, 자격 요건 등)
- 가중치 기반 코사인 유사도 계산
- 유사 기술 스택 가산점 (React ↔ Next.js, FastAPI ↔ Django)

**AI 피드백 생성:**
- 강점(Strengths), 개선점(Weaknesses), 잠재력(Potential) 분석
- 실행 가능한 액션 아이템 제안
- GPT-4o mini 기반 건설적 피드백

### 3. 📚 맞춤형 8주 학습 로드맵

**개인화된 커리큘럼:**
- 스킬 갭 70% 이상 비중으로 부족 역량 집중 학습
- 등급별 차별화된 전략 (D → S 등급까지 맞춤 설계)
- 주차별 3-5개 태스크 + 체크리스트 제공

**큐레이션된 학습 리소스:**
- 80개 이상의 한국어 우선 리소스 매핑
- 난이도별 분류 (초급/중급/고급)
- 플랫폼별 아이콘 (YouTube, 노마드코더, 인프런, MDN 등)

**네트워크 최적화:**
- AI 생성 시간을 고려한 **120초 타임아웃** 설정
- 대용량 요청 처리 안정성 확보

### 4. 🎨 현대적 UI/UX

**Unified Dark Mode:**
- Slate-950 기반 일관된 다크 테마
- ResultPage → RoadmapPage 전체 적용

**Glassmorphism Design:**
- 그라데이션 배경 (`from-slate-900/90 to-slate-950/90`)
- Backdrop blur 효과로 깊이감 표현
- 네온 효과 진행률 바 (`shadow-lg shadow-blue-500/20`)

**한국어 로컬라이제이션:**
- 영문 카테고리 자동 매핑 (`preferred` → `우대 사항`, `experience` → `경력/경험`)
- 카테고리별 색상 코딩 + Lucide React 아이콘 조합
- 사용자 친화적 UX

**인터랙티브 시각화:**
- Recharts Radar Chart (역량 5각형 비교)
- 원형 Match Score 프로그레스 바
- 실시간 태스크 완료 추적

## 데이터 흐름

### 전체 아키텍처
```
1. Frontend (React)
   └─> 파일 업로드 (FormData)
       └─> POST /api/v1/upload
           └─> Backend (FastAPI)
               ├─> PDF 텍스트 추출 (PyPDFLoader)
               ├─> 임베딩 생성 (OpenAI text-embedding-3-small, 1536차원)
               └─> Supabase Vector Store (document_id 기반)
                   └─> pgvector RPC 함수 (코사인 유사도 계산)

2. 매칭 분석
   └─> POST /api/v1/analysis/match (resume_document_id + jd_document_id)
       └─> Backend
           ├─> 벡터 검색 (Supabase RPC)
           ├─> 섹션별 매칭 점수 계산 (가중치 적용)
           ├─> 유사 기술 스택 가산점 (React ↔ Next.js 등)
           └─> GPT-4o mini 피드백 생성
               └─> ResultPage 시각화 (Radar Chart, Match Score)

3. 로드맵 생성
   └─> POST /api/v1/roadmap/generate (resume_id + jd_id, 타임아웃: 120초)
       └─> Backend
           ├─> 스킬 갭 분석
           ├─> GPT-4o mini 기반 8주 커리큘럼 생성
           ├─> 한국어 리소스 매핑 (80+ 리소스)
           └─> RoadmapPage 렌더링
               ├─> 주차별 카드 (체크리스트, 진행률 바)
               └─> ProgressTracker (실시간 완료율)
```

### 주요 최적화
- **재시도 로직**: tenacity를 통한 임베딩 생성 안정화
- **백그라운드 처리**: FastAPI BackgroundTasks로 자동 벡터화
- **타임아웃 관리**: Axios 120초 설정으로 AI 생성 대기 시간 확보
- **데이터 정합성**: document_id 기반 파일-벡터 일대일 매핑

## API 엔드포인트

### 공통
- `GET /` - 루트 엔드포인트
- `GET /health` - 헬스 체크
- `GET /api/v1/health` - API v1 헬스 체크

### 업로드 (Upload)
- `POST /api/v1/upload` - PDF 파일 업로드 및 텍스트 추출 (자동 벡터화 지원)
- `GET /api/v1/upload/health` - 업로드 서비스 헬스 체크

### 분석 (Analysis)
- `POST /api/v1/analysis/ingest` - 문서 벡터화 (수동)
- `POST /api/v1/analysis/match` - 이력서-JD 매칭 분석
  - **Request Body**: `{ resume_document_id, jd_document_id }` ⚠️ `document_id` 필수
  - **Response**: 매칭 점수, 등급, 섹션별 점수, 유사 기술 매칭, AI 피드백
- `POST /api/v1/analysis/gap-analysis` - 스킬 갭 분석 (피드백 포함)
- `GET /api/v1/analysis/documents` - 벡터화된 문서 목록 조회
- `GET /api/v1/analysis/documents/{file_id}` - 문서 상태 조회
- `DELETE /api/v1/analysis/documents/{file_id}` - 문서 삭제
- `GET /api/v1/analysis/health` - 분석 서비스 헬스 체크

### 로드맵 (Roadmap)
- `POST /api/v1/roadmap/generate` - 맞춤형 학습 로드맵 생성 (타임아웃: 120초)
  - **Request Body**: `{ resume_id: document_id, jd_id: document_id, target_weeks: 8 }`
  - **Response**: 8주 커리큘럼, 주차별 태스크, 큐레이션된 리소스, 진행률 추적 데이터
- `GET /api/v1/roadmap/health` - 로드맵 서비스 헬스 체크

## 배포 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    사용자 (Browser)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴─────────────┐
        │                          │
        ▼                          ▼
┌───────────────┐          ┌──────────────┐
│   Frontend    │          │   Backend    │
│   (Vercel)    │◄────────►│   (Fly.io)   │
│               │   CORS   │              │
│ React + Vite  │          │   FastAPI    │
└───────┬───────┘          └──────┬───────┘
        │                         │
        │                         │
        │                  ┌──────┴──────┐
        │                  │             │
        │                  ▼             ▼
        │          ┌─────────────┐  ┌──────────┐
        └─────────►│  Supabase   │  │  OpenAI  │
                   │             │  │          │
                   │ PostgreSQL  │  │ GPT-4o   │
                   │ + pgvector  │  │ Embed    │
                   └─────────────┘  └──────────┘
```

### 주요 배포 특징

**Frontend (Vercel):**
- 자동 HTTPS 및 CDN
- Preview 배포 지원 (PR별)
- 환경 변수 관리
- 무료 티어 (100GB 대역폭/월)

**Backend (Fly.io):**
- Docker 기반 배포
- Auto-scaling (트래픽 없을 때 자동 중지)
- Health check 모니터링
- 무료 티어 (3개 작은 VM)

**CORS 설정:**
- SmartCORSMiddleware로 Vercel 도메인 자동 허용
- Preview 배포 URL도 자동 인식
- 환경 변수로 추가 도메인 관리

---

## 문제 해결 (Troubleshooting)

### 422 Unprocessable Entity 에러

**증상:**
```
POST /api/v1/analysis/match 요청 시 422 에러 발생
```

**원인:**
- 백엔드가 `document_id` (Vector DB 연동 ID)를 기대하는데, 프론트엔드가 `file_id` 전송
- Supabase pgvector에서 document를 찾지 못해 매칭 실패

**해결 방법:**
1. **Backend 응답 구조 확인:**
   - `POST /api/v1/upload` 응답에 `document_id` 포함 확인
   - 응답 예시:
   ```json
   {
     "file_id": "uuid-1234",
     "document_id": "doc-uuid-5678",  // ⚠️ 이 값 사용
     "text": "..."
   }
   ```

2. **Frontend 수정:**
   - `analysisService.ts`에서 `document_id` 사용
   - `ResultPage.tsx`에서 `resume_document_id`, `jd_document_id` 전달
   ```typescript
   navigate(`/roadmap?resume_id=${data.resume_document_id}&jd_id=${data.jd_document_id}`)
   ```

3. **데이터 흐름 검증:**
   - AnalysisPage → 업로드 시 `document_id` 저장
   - ResultPage → API 호출 시 `document_id` 사용
   - RoadmapPage → URL 파라미터로 `document_id` 전달

### 로드맵 생성 타임아웃

**증상:**
```
POST /api/v1/roadmap/generate 요청 시 타임아웃 발생
```

**해결 방법:**
- Axios 타임아웃 120초로 설정 (AI 생성 대기 시간 확보)
```typescript
axios.post('/api/v1/roadmap/generate', data, { timeout: 120000 })
```

### CORS 에러

**증상:**
```
Access to XMLHttpRequest from origin 'https://your-app.vercel.app'
has been blocked by CORS policy
```

**해결 방법:**
1. **Vercel 도메인**: 자동으로 허용됨 (SmartCORSMiddleware)
   - `*.vercel.app` 패턴 자동 인식
   - 별도 설정 불필요

2. **커스텀 도메인**: 환경 변수에 추가
   ```bash
   cd apps/server
   flyctl secrets set ALLOWED_ORIGINS_CSV="http://localhost:3000,https://yourdomain.com"
   ```

3. **상세 가이드**: [CORS_SETUP.md](./apps/server/CORS_SETUP.md) 참조

## 개발 컨벤션

### Git Commit

Conventional Commits 준수:

- `feat:` - 새로운 기능
- `fix:` - 버그 수정
- `docs:` - 문서 수정
- `style:` - 코드 포맷팅
- `refactor:` - 코드 리팩토링
- `test:` - 테스트 추가/수정
- `chore:` - 빌드/설정 변경
- `ai:` - AI/LLM 관련
- `data:` - 데이터 처리 관련

### 코드 품질

- **Frontend**: ESLint + Prettier
- **Backend**: Black + Ruff + mypy
- TypeScript 타입 안정성 확보

## 다음 단계 (Phase별 구현 계획)

### Phase 1: 기본 UI 구조 (✅ 완료)

- [x] 프로젝트 초기 구조
- [x] Frontend/Backend 기본 설정
- [x] 진입점 파일 작성

### Phase 2: 파일 업로드 및 PDF 파싱 (✅ 완료)

- [x] FileUpload 컴포넌트 (react-dropzone) - Frontend
- [x] PDF 텍스트 추출 (PyPDFLoader, pdfplumber) - Backend
- [x] Upload API 엔드포인트 구현 (`POST /api/v1/upload`)
- [x] 텍스트 정제 및 언어 감지
- [x] LangChain Document 변환 (RAG 준비)
- [x] 프론트엔드-백엔드 API 연동 (axios + react-hot-toast)
- [x] 로딩 UI 및 에러 핸들링
- [x] AnalysisPage 구현 (업로드된 데이터 시각화)

### Phase 3: RAG 파이프라인 및 매칭 엔진 (✅ 완료)

- [x] PDF 텍스트 추출 및 전처리 로직 완성
- [x] FastAPI BackgroundTasks를 이용한 자동 벡터 인제션 구현
- [x] Supabase Vector Store (pgvector) 연동 및 재시도 로직 (tenacity) 적용
- [x] 섹션 분류 (Section Classification) 및 가중치 기반 매칭 알고리즘 고도화
- [x] 유사 기술 스택 (Similar Tech Group) 가산점 로직 반영
- [x] 임베딩 생성 (OpenAI text-embedding-3-small, 1536차원)
- [x] 벡터 저장 및 검색 (Supabase pgvector RPC 함수)
- [x] 코사인 유사도 계산 및 매칭 점수/등급 산출
- [x] 스킬 갭 분석 API (`/analysis/gap-analysis`)
- [x] 건설적 피드백 생성 (강점, 개선점, 잠재력, 액션 아이템)

### Phase 4: 로드맵 생성 및 콘텐츠 추천 (✅ 완료)

- [x] GPT-4o mini 기반 AI 로드맵 생성
- [x] 맞춤형 학습 계획 (4-12주 커리큘럼)
- [x] 고퀄리티 한국어 리소스 매핑 (80+ 학습 리소스)
  - 프론트엔드: React, TypeScript, Vue, Next.js, HTML, CSS 등 (30+ 리소스)
  - 백엔드: Node.js, Express, FastAPI, Django, Python 등 (15+ 리소스)
  - 데이터베이스: SQL, PostgreSQL, MongoDB, Redis (10+ 리소스)
  - 도구/인프라: Git, Docker, AWS, Testing (10+ 리소스)
  - 배포: Vercel, Netlify, Deployment (4+ 리소스)
  - 커리어: Portfolio, Resume, Interview 가이드 (10+ 리소스)
- [x] 프론트엔드-백엔드 브릿지 전략 (협업 지식 우선 학습)
- [x] 등급별 로드맵 생성 전략 차별화 (D~S 등급별 맞춤 전략)
- [x] 부족한 기술 70% 이상 비중 학습 계획
- [x] 키워드 표준화 (프론트엔드 아이콘 매핑 최적화: 소문자, 공백 제거)
- [x] 주차별 체크리스트 및 태스크 생성 (3-5개/주)
- [x] 로드맵 생성 API 엔드포인트 (`POST /api/v1/roadmap/generate`)
- [x] 리소스 메타데이터 (platform, difficulty, estimated_hours)
- [x] RoadmapPage 프론트엔드 구현
- [x] TodoChecklist 컴포넌트 구현

### Phase 5: 프론트엔드 시각화 및 로드맵 연동 (✅ 완료)

**로드맵 페이지 구현:**
- [x] TypeScript 타입 정의 (roadmap.types.ts)
- [x] TechIcon 컴포넌트 (키워드 → 아이콘 자동 매핑, lucide-react 활용)
- [x] PlatformIcon 컴포넌트 (플랫폼별 아이콘 표시)
- [x] ProgressTracker 컴포넌트 (전체 및 주차별 진행률 시각화)
- [x] RoadmapWeekCard 컴포넌트 (주차별 학습 계획 카드)
  - 체크리스트 기능 (태스크 완료 토글)
  - 난이도별 배지 (beginner/intermediate/advanced)
  - 우선순위별 색상 코딩 (high/medium/low)
  - 리소스 링크 (플랫폼, 예상 시간 표시)
- [x] RoadmapPage 메인 페이지
  - Axios를 통한 API 호출 (`POST /api/v1/roadmap/generate`, 타임아웃: 120초)
  - 로컬 상태 관리 (태스크 완료 상태 추적)
  - 로딩 스켈레톤 UI
  - 완료 축하 애니메이션
  - 반응형 대시보드 레이아웃 (좌측 진행률, 우측 주차별 카드)

**UX 강화:**
- [x] 로딩 스피너 및 메시지
- [x] 에러 처리 및 사용자 안내
- [x] 실시간 진행률 업데이트
- [x] 완료 시 축하 애니메이션 및 메시지
- [x] Tailwind CSS 기반 현대적 UI 디자인
- [x] **Unified Dark Mode (Slate-950 기반)**
  - ResultPage & RoadmapPage 일관된 다크 테마
  - Glassmorphism 효과 (`bg-gradient-to-br from-slate-900/90 to-slate-950/90`)
  - Backdrop blur 및 네온 진행률 바 (`shadow-lg shadow-blue-500/20`)

**분석 결과 시각화:**
- [x] MatchScore 컴포넌트 (원형 프로그레스 바, 등급별 색상)
- [x] CompetencyChart 컴포넌트 (Recharts Radar Chart, 역량 비교)
- [x] FeedbackSection 컴포넌트 (강점/약점/잠재력/실행계획 시각화)
- [x] ResultPage 완성 (모든 컴포넌트 통합)
- [x] Framer Motion 애니메이션 적용
- [x] App.tsx 라우팅 연동
- [x] AnalysisPage → ResultPage → RoadmapPage 플로우 구성

**한국어 로컬라이제이션:**
- [x] `labelMapper.ts` 유틸리티 구현 (영문 → 한글 자동 매핑)
- [x] 카테고리 배지 한글화 (`preferred` → `우대 사항`, `experience` → `경력/경험`)
- [x] 카테고리별 색상 + 아이콘 조합 (CheckCircle, Star, Briefcase, Zap, Code)
- [x] ResultPage & RoadmapPage 일관된 용어 사용

**데이터 정합성 강화:**
- [x] `file_id` → `document_id` 전환으로 422 에러 해결
- [x] Vector DB 연동 ID 기반 아키텍처
- [x] AnalysisPage, ResultPage, RoadmapPage 전체 `document_id` 사용

### Phase 6: 배포 및 최적화 (✅ 완료)

**배포:**
- [x] Vercel 배포 (Frontend)
  - Production URL: https://web-kostiszxr-heyjunns-projects.vercel.app
  - SPA 라우팅 설정 (vercel.json)
  - 환경 변수 관리 (VITE_API_BASE_URL, VITE_SUPABASE_*)
  - 자동 배포 스크립트 (deploy-vercel.ps1)
- [x] Fly.io 배포 (Backend)
  - Production URL: https://jd-vector-api.fly.dev
  - Multi-stage Dockerfile (Poetry 기반)
  - 헬스체크 설정 (30초 간격)
  - Auto-scaling 설정 (min_machines_running: 0)
  - 자동 배포 스크립트 (deploy.ps1)

**보안 강화:**
- [x] CORS 정책 최적화
  - SmartCORSMiddleware 구현
  - Vercel 도메인(*.vercel.app) 자동 인식
  - Preflight 요청 캐싱 (10분)
  - 환경 변수 기반 도메인 관리
- [x] 환경 변수 보안 검증
  - .env.example 템플릿 제공
  - Fly.io Secrets 사용
  - Vercel Environment Variables 사용
- [x] TypeScript 타입 안정성
  - 빌드 에러 제로화
  - Recharts 타입 호환성 개선
  - 미사용 변수 제거

**문서화:**
- [x] 배포 가이드 작성 (DEPLOYMENT.md, DEPLOYMENT_VERCEL.md)
- [x] CORS 설정 가이드 (CORS_SETUP.md)
- [x] 빠른 시작 가이드 (QUICKSTART.md)
- [x] 자동화 스크립트 (PowerShell)

**성능 최적화:**
- [x] React.lazy + Suspense 기반 코드 스플리팅 (페이지별 청크 분리)
- [x] Vite manual chunk 설정으로 번들 최적화
  - `react-vendor`, `charts`, `icons`, `utils` 청크 수동 분리
- [x] API 응답 캐싱 레이어 구현 (`apiCache.ts`)
  - TTL 기반 메모리 캐시 (기본 5분)
  - 중복 API 호출 방지

---

### Phase 7: 코드 품질 향상 및 구조 최적화 (✅ 완료)

기능 변경 없이 코드 품질과 유지보수성을 개선하는 리팩토링 작업.

**불필요한 자원 정리:**
- [x] 미구현 빈 스텁 파일 40개 삭제
  - `components/ui/`, `components/layout/`, `components/common/`
  - `hooks/`, `store/`, `services/`, `types/`, `utils/` 의 미사용 플레이스홀더
- [x] 백엔드 미사용 코드 제거
  - `upload_service.py` — `import shutil` 미사용 import 제거
  - `upload_service.py` — Phase 3 미구현 Supabase Storage 함수 2개 제거
    (`upload_to_supabase_storage`, `delete_from_supabase_storage`)

**디버그 로그 정리:**
- [x] `ResultPage.tsx` — 프로덕션 노출 `console.log` 4개 제거
- [x] `apiCache.ts` — 캐시 히트/미스 로그를 `import.meta.env.DEV` 조건부 처리
- [x] `upload.py` — `print()` 디버그 출력 15개를 표준 `logger` 호출로 교체
  (`logger.info`, `logger.debug`, `logger.warning`, `logger.error`)

**공통 컴포넌트 추출 (중복 제거):**
- [x] `components/ui/StatCard.tsx` — `AnalysisPage`·`ResultPage` 중복 구현 통합
  - color prop 미제공 시 slate 정적 스타일, 제공 시 컬러 + Framer Motion 애니메이션
- [x] `components/analysis/feedbackConfig.ts` — `FeedbackSection`·`FeedbackCard` 공유 설정 분리
  - `sectionConfig`, `FeedbackItem` 인터페이스, `isString` 헬퍼

**컴포넌트 분리 (300줄 이상 파일 축소):**

| 원본 파일 | 분리된 파일 | 줄 감소 |
|-----------|------------|--------|
| `AnalysisPage.tsx` (347줄) | `components/analysis/DocumentPanel.tsx` | -142줄 |
| `FeedbackSection.tsx` (269줄) | `components/analysis/FeedbackCard.tsx` | -157줄 |
| `UploadPage.tsx` (312줄) | `components/upload/UploadLoadingOverlay.tsx`<br>`components/upload/UploadProgressSteps.tsx` | -82줄 |
| `RoadmapWeekCard.tsx` (216줄) | `components/roadmap/RoadmapResourceItem.tsx` | -51줄 |
| `ResultPage.tsx` (323줄) | `utils/scoreNormalization.ts` | -58줄 |

**유틸리티 추출:**
- [x] `utils/scoreNormalization.ts` — 0-1/0-100 혼용 점수를 0-100 정수로 정규화
  - 백엔드 응답 범위 자동 감지 + 클램핑 처리

---

### 향후 계획

**추가 기능:**
- [ ] Supabase Storage 연동 (파일 영구 저장)
- [ ] API Rate Limiting
- [ ] 모니터링 및 로깅
  - [ ] Sentry 연동 (에러 추적)
  - [ ] Analytics 통합 (사용자 행동 분석)

## 라이선스

MIT License

## 기여

기여를 환영합니다! Pull Request를 보내주세요.

## 문의

프로젝트에 대한 문의는 Issue를 통해 남겨주세요.
