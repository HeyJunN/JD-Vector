"""
JD-Vector Backend - FastAPI Application Entry Point
"""

from fastapi import FastAPI
from app.core.config import settings
from app.core.cors import SmartCORSMiddleware
from app.api.v1.router import api_router

app = FastAPI(
    title="JD-Vector API",
    description="AI-powered Job Description Analyzer and Career Roadmap Generator",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 스마트 CORS 설정
# Vercel 도메인 패턴을 자동으로 인식하여 허용합니다.
app.add_middleware(
    SmartCORSMiddleware,
    allowed_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """루트 엔드포인트 - API 상태 확인"""
    return {
        "message": "JD-Vector API is running",
        "version": "0.1.0",
        "status": "healthy",
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "ok"}


# API 라우터 등록
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
