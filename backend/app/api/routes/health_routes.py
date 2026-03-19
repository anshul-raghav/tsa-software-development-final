"""
Health check route: GET /health for liveness/readiness.
"""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "TouchMap API"}
