# backend/app/api/v1/webhooks.py
"""
Internal-only callbacks posted by the agent orchestrator.
Protected by a shared secret in X-Internal-Token header.
This endpoint is never exposed through the public ingress.
"""
import os

from fastapi import APIRouter, Header, HTTPException, status

from app.models.agent_result import AgentResult, AgentErrorResult
from app.services.redis_client import async_redis
from app.services.session import SessionService

router     = APIRouter(prefix="/internal", tags=["webhooks"])
_INT_TOKEN = os.getenv("INTERNAL_WEBHOOK_TOKEN", "")


def _check(token: str) -> None:
    if not _INT_TOKEN or token != _INT_TOKEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid internal token")


@router.post("/agent-result")
async def receive_agent_result(
    payload:          AgentResult,
    x_internal_token: str = Header(),
) -> dict:
    """Called by the orchestrator on pipeline success."""
    _check(x_internal_token)
    await SessionService(async_redis).apply_agent_result(payload)
    return {"ok": True, "case_id": payload.case_id}


@router.post("/agent-error")
async def receive_agent_error(
    payload:          AgentErrorResult,
    x_internal_token: str = Header(),
) -> dict:
    """Called by the orchestrator on pipeline failure."""
    _check(x_internal_token)
    await SessionService(async_redis).apply_agent_error(payload)
    return {"ok": True, "case_id": payload.case_id}