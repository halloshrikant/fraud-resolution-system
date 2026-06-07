# backend/app/api/v1/health.py
from fastapi import APIRouter
from app.services.redis_client import async_redis

router = APIRouter()


@router.get("/health", tags=["health"])
async def liveness() -> dict:
    """Kubernetes liveness probe — returns 200 if the process is alive."""
    return {"status": "ok"}


@router.get("/ready", tags=["health"])
async def readiness() -> dict:
    """Kubernetes readiness probe — verifies Redis connectivity."""
    await async_redis.ping()
    return {"status": "ready"}