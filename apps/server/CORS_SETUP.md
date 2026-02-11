# CORS 설정 가이드

이 문서는 JD-Vector 백엔드의 CORS 설정을 관리하는 방법을 설명합니다.

## 개요

JD-Vector는 **SmartCORSMiddleware**를 사용하여 CORS를 자동으로 관리합니다.

### 주요 기능

1. ✅ **Vercel 도메인 자동 인식**
   - 모든 `*.vercel.app` 도메인이 자동으로 허용됩니다
   - Preview 배포, Production 배포 모두 지원
   - 별도 설정 없이 Vercel 배포 즉시 사용 가능

2. ✅ **환경 변수 기반 설정**
   - `ALLOWED_ORIGINS_CSV` 환경 변수로 추가 도메인 지정
   - 쉼표로 구분된 문자열 형식
   - 공백 자동 제거

3. ✅ **Preflight 요청 최적화**
   - OPTIONS 요청을 효율적으로 처리
   - 10분간 Preflight 결과 캐싱 (`Access-Control-Max-Age: 600`)

---

## 자동으로 허용되는 도메인

### Vercel 도메인 (자동)

다음 패턴의 모든 도메인이 **자동으로 허용**됩니다:

```
https://*.vercel.app
http://*.vercel.app
```

**예시:**
- ✅ `https://web-kostiszxr-heyjunns-projects.vercel.app`
- ✅ `https://web-ten-phi-56.vercel.app`
- ✅ `https://my-app-abc123.vercel.app`
- ✅ `https://jd-vector-web.vercel.app`

### 환경 변수로 지정된 도메인

`ALLOWED_ORIGINS_CSV` 환경 변수에 명시된 도메인들도 허용됩니다.

---

## Fly.io 환경 변수 설정

### 현재 설정 확인

```bash
cd apps/server
flyctl secrets list
```

### 기본 설정 (개발 환경 포함)

Vercel 도메인은 자동으로 허용되므로, localhost만 추가하면 됩니다:

```bash
flyctl secrets set ALLOWED_ORIGINS_CSV="http://localhost:3000,http://localhost:5173"
```

### 커스텀 도메인 추가

커스텀 도메인을 사용하는 경우:

```bash
flyctl secrets set ALLOWED_ORIGINS_CSV="http://localhost:3000,http://localhost:5173,https://yourdomain.com"
```

### 여러 도메인 설정 예시

```bash
flyctl secrets set ALLOWED_ORIGINS_CSV="http://localhost:3000,http://localhost:5173,https://jd-vector.com,https://app.jd-vector.com"
```

---

## CORS 동작 방식

### 1. Origin 검증 순서

SmartCORSMiddleware는 다음 순서로 Origin을 검증합니다:

1. **명시적 허용 목록 확인**
   - `ALLOWED_ORIGINS_CSV`에 포함된 도메인인지 확인

2. **Vercel 패턴 매칭**
   - `*.vercel.app` 패턴과 일치하는지 확인 (정규식 사용)

3. **허용 또는 거부**
   - 위 조건 중 하나라도 만족하면 허용
   - 모두 만족하지 않으면 거부

### 2. Preflight 요청 처리

`OPTIONS` 메서드 요청 시:

```
Access-Control-Allow-Origin: <request-origin>
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
Access-Control-Allow-Headers: *
Access-Control-Max-Age: 600
```

### 3. 실제 요청 처리

일반 요청(GET, POST 등) 시:

```
Access-Control-Allow-Origin: <request-origin>
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
Access-Control-Allow-Headers: *
```

---

## 로컬 개발 환경 설정

### .env 파일 생성

```bash
cd apps/server
cp .env.example .env
```

### .env 파일 수정

```env
ENVIRONMENT=development

# CORS 설정
ALLOWED_ORIGINS_CSV=http://localhost:3000,http://localhost:5173

# 기타 필수 환경 변수들...
```

### 로컬 서버 실행

```bash
poetry run uvicorn main:app --reload
```

---

## 프로덕션 배포 후 확인

### 1. CORS 테스트 (브라우저 Console)

Vercel 배포 URL에서 브라우저 개발자 도구를 열고:

```javascript
// 백엔드 헬스체크 API 호출
fetch('https://jd-vector-api.fly.dev/health')
  .then(res => res.json())
  .then(data => console.log('✅ CORS OK:', data))
  .catch(err => console.error('❌ CORS Error:', err))
```

### 2. 예상 결과

**성공 시:**
```json
{
  "status": "ok"
}
```

**실패 시 (CORS 에러):**
```
Access to fetch at 'https://jd-vector-api.fly.dev/health' from origin
'https://your-app.vercel.app' has been blocked by CORS policy
```

### 3. 백엔드 로그 확인

```bash
flyctl logs
```

프로덕션 환경에서는 허용된 origins가 로그에 출력됩니다:

```
Configured ALLOWED_ORIGINS: ['http://localhost:3000', 'http://localhost:5173']
Note: All *.vercel.app domains are automatically allowed by SmartCORSMiddleware
```

---

## 트러블슈팅

### 문제 1: Vercel 도메인에서 CORS 에러

**증상:**
```
Access to XMLHttpRequest at 'https://jd-vector-api.fly.dev/api/v1/...'
from origin 'https://my-app.vercel.app' has been blocked by CORS policy
```

**해결:**
1. 백엔드가 최신 코드로 배포되었는지 확인:
   ```bash
   cd apps/server
   flyctl deploy
   ```

2. SmartCORSMiddleware가 적용되었는지 확인:
   ```bash
   flyctl logs
   ```

3. Vercel 도메인이 `*.vercel.app` 패턴과 일치하는지 확인

### 문제 2: 커스텀 도메인에서 CORS 에러

**증상:**
```
Access to XMLHttpRequest from origin 'https://mycustomdomain.com' has been blocked
```

**해결:**
커스텀 도메인은 자동으로 허용되지 않으므로 환경 변수에 추가:

```bash
flyctl secrets set ALLOWED_ORIGINS_CSV="http://localhost:3000,https://mycustomdomain.com"
```

### 문제 3: Preflight 요청 실패

**증상:**
브라우저 Network 탭에서 OPTIONS 요청이 실패

**해결:**
1. `allow_methods`에 필요한 메서드가 포함되어 있는지 확인
2. `allow_headers`가 `["*"]`로 설정되어 있는지 확인
3. 백엔드 재배포:
   ```bash
   flyctl deploy
   ```

### 문제 4: 환경 변수 형식 오류

**증상:**
환경 변수가 제대로 파싱되지 않음

**해결:**
1. 쉼표로 구분되어 있는지 확인
2. 각 URL이 프로토콜(http:// 또는 https://)을 포함하는지 확인
3. 불필요한 공백 제거 (자동으로 제거되지만 확인)

**올바른 형식:**
```bash
flyctl secrets set ALLOWED_ORIGINS_CSV="http://localhost:3000,https://app.example.com"
```

**잘못된 형식:**
```bash
flyctl secrets set ALLOWED_ORIGINS_CSV="localhost:3000, app.example.com"
# ❌ 프로토콜 누락
```

---

## 보안 고려사항

### 1. Wildcard 사용 주의

현재 구현은 `*.vercel.app` 패턴을 허용합니다. 이는 편의성을 위한 것이지만, 보안을 강화하려면:

**옵션 A: 특정 Vercel 도메인만 허용**

`app/core/cors.py` 수정:

```python
# Vercel 자동 인식 비활성화
def is_origin_allowed(self, origin: str) -> bool:
    # 명시적 리스트만 허용
    return origin in self.allowed_origins
```

환경 변수에 모든 도메인 명시:

```bash
flyctl secrets set ALLOWED_ORIGINS_CSV="http://localhost:3000,https://web-ten-phi-56.vercel.app,https://jd-vector-web.vercel.app"
```

**옵션 B: 서브도메인 제한**

특정 Vercel 프로젝트만 허용:

```python
# 정규식 패턴 수정
self.vercel_pattern = re.compile(
    r'^https?://jd-vector-web(-[a-zA-Z0-9]+)?\.vercel\.app$'
)
```

### 2. Credentials 사용

`allow_credentials=True`로 설정되어 있어 쿠키, 인증 헤더 등을 허용합니다.

인증이 필요하지 않다면 `False`로 변경:

```python
# main.py
app.add_middleware(
    SmartCORSMiddleware,
    allowed_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,  # 변경
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)
```

### 3. 허용 메서드 제한

현재는 모든 HTTP 메서드를 허용합니다. 필요한 메서드만 허용하려면:

```python
# main.py
allow_methods=["GET", "POST", "OPTIONS"],  # PUT, DELETE 제거
```

---

## 코드 구조

### 파일 위치

```
apps/server/
├── app/
│   └── core/
│       ├── cors.py          # SmartCORSMiddleware 구현
│       └── config.py        # ALLOWED_ORIGINS 설정
├── main.py                  # CORS 미들웨어 등록
└── .env.example             # 환경 변수 예시
```

### SmartCORSMiddleware 클래스

**주요 메서드:**

1. `__init__`: 초기화 및 Vercel 패턴 정규식 설정
2. `is_origin_allowed`: Origin 검증 로직
3. `dispatch`: Preflight 및 실제 요청 처리

**사용 예시:**

```python
from app.core.cors import SmartCORSMiddleware

app.add_middleware(
    SmartCORSMiddleware,
    allowed_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## FAQ

### Q1: Vercel Preview 배포도 자동으로 허용되나요?

**A:** 네, `*.vercel.app` 패턴과 일치하는 모든 도메인이 허용됩니다.
- ✅ Production: `https://jd-vector-web.vercel.app`
- ✅ Preview: `https://jd-vector-web-abc123.vercel.app`
- ✅ Branch 배포: `https://jd-vector-web-git-feature-branch.vercel.app`

### Q2: 환경 변수 변경 후 재배포가 필요한가요?

**A:** Fly.io secrets 변경 시 자동으로 재시작됩니다:

```bash
flyctl secrets set ALLOWED_ORIGINS_CSV="..."
# 자동으로 앱이 재시작됩니다
```

### Q3: localhost:8000에서 테스트하려면?

**A:** `.env` 파일에 추가:

```env
ALLOWED_ORIGINS_CSV=http://localhost:3000,http://localhost:5173,http://localhost:8000
```

### Q4: HTTP와 HTTPS 모두 허용하나요?

**A:** 네, 정규식 패턴이 `https?://`를 사용하므로 둘 다 허용됩니다.
- ✅ `http://my-app.vercel.app`
- ✅ `https://my-app.vercel.app`

### Q5: IP 주소는 허용되나요?

**A:** 환경 변수에 명시적으로 추가하면 허용됩니다:

```bash
flyctl secrets set ALLOWED_ORIGINS_CSV="http://localhost:3000,http://192.168.1.100:3000"
```

---

## 참고 자료

- [FastAPI CORS 문서](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN CORS 가이드](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Vercel 도메인 문서](https://vercel.com/docs/concepts/deployments/domains)
- [Fly.io Secrets 관리](https://fly.io/docs/reference/secrets/)

---

## 변경 이력

- **2024-01-XX**: SmartCORSMiddleware 도입, Vercel 도메인 자동 인식 추가
- **2024-01-XX**: Preflight 캐싱 최적화 (Access-Control-Max-Age: 600)
- **2024-01-XX**: 환경 변수 파싱 개선 (공백 제거, 빈 문자열 필터링)
