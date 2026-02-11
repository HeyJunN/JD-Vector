# Multi-stage build for Python FastAPI application
FROM python:3.11-slim as builder

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치
ENV POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

# 의존성 파일만 먼저 복사 (캐싱 최적화)
COPY pyproject.toml poetry.lock* ./

# 프로덕션 의존성만 설치 (dev 제외)
RUN poetry install --without dev,data --no-root && rm -rf $POETRY_CACHE_DIR

# Runtime stage
FROM python:3.11-slim as runtime

# 런타임 의존성 설치
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 가상환경을 builder에서 복사
COPY --from=builder /app/.venv /app/.venv

# 애플리케이션 코드 복사
COPY . .

# 가상환경 활성화
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 포트 설정
EXPOSE 8080

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# uvicorn으로 FastAPI 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
