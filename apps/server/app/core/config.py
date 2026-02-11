"""
Application Configuration using Pydantic Settings
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    # Environment
    ENVIRONMENT: str = "development"

    # API
    API_V1_PREFIX: str = "/api/v1"

    # CORS - 환경 변수로 유연하게 설정
    ALLOWED_ORIGINS_CSV: str = "http://localhost:3000,http://localhost:5173"

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """
        쉼표로 구분된 문자열을 리스트로 변환
        예: "https://app.vercel.app,https://example.com" -> ["https://app.vercel.app", "https://example.com"]

        참고: Vercel 도메인(*.vercel.app)은 SmartCORSMiddleware에서 자동으로 허용됩니다.
        """
        if not self.ALLOWED_ORIGINS_CSV:
            return []

        # 공백 제거 및 정제
        origins = [origin.strip() for origin in self.ALLOWED_ORIGINS_CSV.split(",") if origin.strip()]

        # 프로덕션 환경에서는 로깅
        if self.is_production:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Configured ALLOWED_ORIGINS: {origins}")
            logger.info("Note: All *.vercel.app domains are automatically allowed by SmartCORSMiddleware")

        return origins

    # OpenAI
    OPENAI_API_KEY: str = ""

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""

    # Database
    DATABASE_URL: str = ""
    DATABASE_ECHO: bool = False

    # Embedding Model
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    # LLM Model
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.3

    # File Upload
    MAX_UPLOAD_SIZE: int = 20971520  # 20MB
    ALLOWED_FILE_TYPES: List[str] = [
        "application/pdf",
        "text/plain",
        "text/markdown",
    ]

    # Vector Store
    VECTOR_STORE_TYPE: str = "supabase"  # supabase or chromadb
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def is_development(self) -> bool:
        """개발 환경 여부"""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부"""
        return self.ENVIRONMENT == "production"


# 싱글톤 인스턴스
settings = Settings()
