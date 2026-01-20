# JD-Vector

AI 기반 직무 적합도 분석 및 커리어 로드맵 서비스

특정 채용 공고와 지원자가 지닌 기술 스택 간의 간극을 데이터로 분석하고, 최적의 학습 로드맵을 제시합니다.

## 프로젝트 개요

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + LangChain + Python 3.11
- **Database**: Supabase (PostgreSQL + pgvector)
- **AI/LLM**: OpenAI GPT-4o mini, text-embedding-3-small
- **Utilities**: tenacity (재시도 로직), tiktoken (토큰 계산)
- **배포**: Vercel (Frontend), Fly.io (Backend)

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

### 1. 멀티 소스 데이터 업로드

- 이력서 PDF 및 프로젝트 경험 입력
- 채용 공고(JD) 텍스트/PDF 업로드

### 2. RAG 기반 분석

- LangChain을 활용한 핵심 기술 스택 추출
- 벡터 유사도(Cosine Similarity) 계산
- 역량별 매칭도 분석

### 3. AI 로드맵 생성

- 부족한 역량 보완을 위한 학습 계획 제안
- 구체적이고 실행 가능한 프로젝트 기능 추가 가이드

### 4. 시각화

- Radar Chart로 역량 오각형 표시
- Match Score 및 등급 표시
- 인터랙티브 로드맵 체크리스트

## 데이터 흐름

1. **Frontend**: 파일 업로드 (FormData)
2. **Backend**: PDF 텍스트 추출 (PyPDFLoader/pdfplumber)
3. **임베딩 생성**: OpenAI text-embedding-3-small (1536차원)
4. **벡터 저장**: Supabase pgvector
5. **유사도 계산**: scikit-learn cosine_similarity
6. **LLM 분석**: GPT-4o mini (기술 스택 추출, 간극 분석)
7. **로드맵 생성**: AI 에이전트 (3개월 학습 계획)
8. **시각화**: Recharts Radar Chart, Match Score

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
- `POST /api/v1/analysis/gap-analysis` - 스킬 갭 분석 (피드백 포함)
- `GET /api/v1/analysis/documents` - 벡터화된 문서 목록 조회
- `GET /api/v1/analysis/documents/{file_id}` - 문서 상태 조회
- `DELETE /api/v1/analysis/documents/{file_id}` - 문서 삭제
- `GET /api/v1/analysis/health` - 분석 서비스 헬스 체크

### 로드맵 (Roadmap)
- `POST /api/v1/roadmap/generate` - 맞춤형 학습 로드맵 생성
- `GET /api/v1/roadmap/health` - 로드맵 서비스 헬스 체크

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
- [ ] RoadmapPage 프론트엔드 구현 (Phase 5로 이동)
- [ ] TodoChecklist 컴포넌트 구현 (Phase 5로 이동)

### Phase 5: 분석 결과 시각화

- [ ] RadarChart 컴포넌트 (Recharts)
- [ ] MatchScore 컴포넌트
- [ ] ResultPage 완성
- [ ] 피드백 UI (강점/약점/잠재력 시각화)

### Phase 6: 배포 및 최적화

- [ ] Vercel 배포 (Frontend)
- [ ] Fly.io 배포 (Backend)
- [ ] 성능 최적화
- [ ] Supabase Storage 연동 (파일 영구 저장)

## 라이선스

MIT License

## 기여

기여를 환영합니다! Pull Request를 보내주세요.

## 문의

프로젝트에 대한 문의는 Issue를 통해 남겨주세요.
