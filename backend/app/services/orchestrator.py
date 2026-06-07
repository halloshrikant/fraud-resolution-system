# backend/app/services/orchestrator.py
"""
Bridges FastAPI to the agent pipeline.
In the PoC, agents are imported directly (monorepo / shared PYTHONPATH).
In production, replace the agent call with an async HTTP/queue message.
"""
import time

from app.models.dispute import DisputeRequest
from app.models.agent_result import AgentResult, AgentErrorResult
from app.services.session import SessionService
from app.services.redis_client import async_redis

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
async def run_dispute_pipeline(payload: DisputeRequest, case_id: str) -> None:
    """Called as a FastAPI BackgroundTask."""
    session = SessionService(async_redis)
    start   = time.monotonic()

    try:
        from fraud_agents.orchestrator.agent import run_dispute_pipeline as _agent_run
        from fraud_agents.shared.mlflow_tracker import MLflowSpanTracker
        from fraud_agents.shared.pydantic_models import DisputeRequest as AgentRequest

        agent_payload = AgentRequest(
            case_id            = case_id,
            customer_id        = payload.customer_id,
            transaction_id     = payload.transaction_id,
            dispute_reason     = payload.dispute_reason,
            dispute_amount_usd = payload.dispute_amount_usd,
        )

        with MLflowSpanTracker(case_id) as tracker:
            result = await _agent_run(agent_payload, tracker)

        agent_result = AgentResult(
            case_id             = case_id,
            risk_score          = result.risk_score,
            risk_level          = result.risk_level,
            resolution_action   = result.resolution_action,
            agent_rationale     = result.agent_rationale,
            evidence_flags      = result.evidence_flags,
            applicable_policies = result.applicable_policies,
            processing_time_ms  = (time.monotonic() - start) * 1000,
        )
        await session.apply_agent_result(agent_result)

    except Exception as exc:
        await session.apply_agent_error(AgentErrorResult(
            case_id      = case_id,
            error_code   = type(exc).__name__,
            error_detail = str(exc)[:500],
            retryable    = True,
        ))
        raise