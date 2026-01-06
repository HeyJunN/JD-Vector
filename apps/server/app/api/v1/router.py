"""
API v1 Router - Aggregates all endpoint routers
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, upload
# from app.api.v1.endpoints import analysis, roadmap

api_router = APIRouter()

# Health check endpoint
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Upload endpoint (Phase 2)
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])

# Additional routers (to be implemented)
# api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
# api_router.include_router(roadmap.router, prefix="/roadmap", tags=["roadmap"])
