"""
Health Check Endpoints
"""

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str
    timestamp: datetime
    version: str
    environment: str


@router.get("", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Returns:
        HealthResponse: Current API health status
    """
    from app.core.config import settings

    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="0.1.0",
        environment=settings.ENVIRONMENT,
    )


@router.get("/ping")
async def ping():
    """
    Simple ping endpoint

    Returns:
        dict: Pong response
    """
    return {"message": "pong"}
