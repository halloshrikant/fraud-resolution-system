"""
Fraud Resolution System - FastAPI Backend

This is the main entry point for the fraud resolution API.
Provides endpoints for dispute submission, case status tracking, and analyst dashboard.

Architecture:
- FastAPI for REST API
- Redis for session/case storage and vector search
- AWS Bedrock (via LiteLLM) for AI agents
- MLflow for experiment tracking
- AWS Cognito for authentication (bypassed in DEV_MODE)

Author: Fraud Prevention Team
Version: 1.0.0
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import disputes, dashboard, health
from app.middleware.auth import JWTAuthMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.logging import StructuredLoggingMiddleware
from app.services.redis_client import async_redis
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Startup:
        - Verify Redis connectivity
        - Initialize connection pools
    
    Shutdown:
        - Gracefully close Redis connections
        - Clean up resources
    """
    # Startup: verify Redis connectivity
    await async_redis.ping()
    print("✓ Redis connection established")
    
    yield
    
    # Shutdown: graceful close
    await async_redis.aclose()
    print("✓ Redis connection closed")


app = FastAPI(
    title="Fraud Resolution API",
    version="1.0.0",
    description="AI-powered fraud dispute resolution system with multi-agent orchestration",
    # Enable docs in dev mode, disable in production
    docs_url="/docs" if settings.DEV_MODE else None,
    redoc_url="/redoc" if settings.DEV_MODE else None,
    lifespan=lifespan,
)

# Security headers — OWASP hardening
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,   # Strict allowlist
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)
app.add_middleware(JWTAuthMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
app.add_middleware(StructuredLoggingMiddleware)

app.include_router(disputes.router,  prefix="/api/v1", tags=["disputes"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["dashboard"])
app.include_router(health.router,    tags=["health"])


@app.get("/")
async def root():
    """
    Root endpoint - API information and available routes.
    
    Returns:
        dict: API metadata and endpoint links
    """
    return {
        "name": "Fraud Resolution API",
        "version": "1.0.0",
        "status": "operational",
        "mode": "development" if settings.DEV_MODE else "production",
        "endpoints": {
            "health": "/health",
            "docs": "/docs" if settings.DEV_MODE else "disabled",
            "submit_dispute": "POST /api/v1/dispute",
            "stream_status": "GET /api/v1/dispute/{case_id}/stream",
            "dashboard": "GET /api/v1/dashboard/cases",
        },
    }