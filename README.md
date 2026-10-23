# JD-Vector

**AI 기반 직무 적합도 분석 및 맞춤형 커리어 로드맵 서비스**

RAG(Retrieval-Augmented Generation) 파이프라인을 활용하여 채용 공고(JD)와 지원자 이력서 간의 스킬 갭을 정밀 분석하고, 개인화된 8주 학습 커리큘럼을 자동 생성합니다.

## 프로젝트 개요

### 핵심 가치
- **데이터 정합성**: Vector DB와 연동된 `document_id` 기반 아키텍처로 파일-벡터 간 일관성 보장
- **AI 기반 분석**: GPT-4o mini와 임베딩 모델을 활용한 섹션별 역량 매칭 및 피드백 생성
- **실행 가능한 로드맵**: 부족 역량 70% 이상 집중 학습 + 80개 이상의 큐레이션된 한국어 리소스 제공

### 기술 스택

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

## 배포된 서비스

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

## 기능

<h3 align="center">이력서 및 채용 공고(JD) 업로드</h3>

<div align="center">
  <table>
    <tr>
      <td align="center">
          <img width="1920" height="860" alt="본인의 이력서와 지원하고자 하는 기업의 채용공고 업로드" src="https://github.com/user-attachments/assets/aaa27017-87c8-4d4b-b57f-cd579fd9e841" />
      </td>
    </tr>
    <tr>
      <td align="center"><b>본인의 이력서와 지원하고자 하는 기업의 채용공고 업로드</b></td>
    </tr>
  </table>
</div>

<h3 align="center">문서 파싱 및 텍스트 추출 검증</h3>

<div align="center">
  <table>
    <tr>
      <td align="center">
          <img width="1920" height="860" alt="업로드된 문서의 페이지 수, 단어수, 추출된 텍스트 본문 확인 후 검증" src="https://github.com/user-attachments/assets/754d26b2-d587-477e-8803-2e01ffbf7f84" />
      </td>
    </tr>
    <tr>
      <td align="center"><b>업로드된 문서의 페이지 수, 단어수, 추출된 텍스트 본문 확인 후 검증</b></td>
    </tr>
  </table>
</div>

<h3 align="center">AI 적합도 분석 및 매칭 점수 대시보드</h3>

<div align="center">
  <table>
    <tr>
      <td align="center">
          <img width="1920" height="860" alt="벡터 유사도 분석 기반 산출된 종합 점수 요약" src="https://github.com/user-attachments/assets/c332b4d7-5819-4237-b094-935ecef6f819" />
      </td>
    </tr>
    <tr>
      <td align="center"><b>벡터 유사도 분석 기반 산출된 종합 점수 요약</b></td>
    </tr>
  </table>
</div>

<h3 align="center">역량 비교분석</h3>

<div align="center">
  <table>
    <tr>
      <td align="center">
          <img width="1920" height="860" alt="기업 목표 역량 수준과 이력서의 매칭도를 방사형 차트로 시각화" src="https://github.com/user-attachments/assets/b98dff1e-c1b2-4a19-b872-0471bc90fc2b" />
      </td>
    </tr>
    <tr>
      <td align="center"><b>기업 목표 역량 수준과 이력서의 매칭도를 방사형 차트로 시각화</b></td>
    </tr>
  </table>
</div>

<h3 align="center">AI 종합 분석 및 맞춤형 실행 계획</h3>

<div align="center">
  <table>
    <tr>
      <td align="center">
          <img width="1920" height="860" alt="분석 결과를 바탕으로 보완사항과 실행 계획 제안" src="https://github.com/user-attachments/assets/9da9bf0f-1699-4200-ba0f-355e620eafea" />
      </td>
    </tr>
    <tr>
      <td align="center"><b>분석 결과를 바탕으로 보완사항과 실행 계획 제안</b></td>
    </tr>
  </table>
</div>

<h3 align="center">맞춤형 학습 로드맵 및 주차별 태스크</h3>

<div align="center">
  <table>
    <tr>
      <td align="center">
          <img width="1920" height="860" alt="부족한 역량을 채우기 위한 8주 커리큘럼 기반 학습 전략과 테스크 체크리스트" src="https://github.com/user-attachments/assets/8a741655-e1e0-4e83-ae28-bf5b8a24aa99" />
      </td>
    </tr>
    <tr>
      <td align="center"><b>부족한 역량을 채우기 위한 8주 커리큘럼 기반 학습 전략과 테스크 체크리스트</b></td>
    </tr>
  </table>
</div>

## 핵심 기술

### 1. Document ID 기반 RAG 파이프라인

**데이터 정합성 보장:**
- 단순 `file_id`가 아닌 **Vector DB 연동 `document_id`** 사용
- Supabase pgvector와 완벽한 동기화로 데이터 불일치 방지
- API 422 에러 원천 차단 (파일-벡터 매핑 무결성)

**자동 벡터화:**
- PDF 업로드 시 BackgroundTasks를 통한 자동 임베딩 생성
- OpenAI text-embedding-3-small (1536차원) 활용
- tenacity 기반 재시도 로직으로 안정성 확보

### 2. 섹션별 스킬 갭 분석

**정밀 매칭 알고리즘:**
- 이력서와 JD를 섹션별로 분류 (기술 스택, 경험, 자격 요건 등)
- 가중치 기반 코사인 유사도 계산
- 유사 기술 스택 가산점 (React ↔ Next.js, FastAPI ↔ Django)

**AI 피드백 생성:**
- 강점(Strengths), 개선점(Weaknesses), 잠재력(Potential) 분석
- 실행 가능한 액션 아이템 제안
- GPT-4o mini 기반 건설적 피드백

### 3. 맞춤형 8주 학습 로드맵

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

### 4. 현대적 UI/UX

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

## 문의

프로젝트에 대한 문의는 Issue를 통해 남겨주세요.
