# backend/app/services/session.py
import json
import uuid
from datetime import datetime, timezone
from typing import AsyncIterator

from redis.asyncio import Redis

from app.models.dispute import DisputeRequest, CaseStatus
from app.models.agent_result import AgentResult, AgentErrorResult

_STREAM_TTL = 3600        # 1 hour SSE stream TTL
_CASE_TTL   = 86400 * 30  # 30-day case retention


class SessionService:
    def __init__(self, redis: Redis) -> None:
        self._r = redis

    # ── Case Creation ─────────────────────────────────────────────────
    async def create_case(self, payload: DisputeRequest) -> str:
        case_id = str(uuid.uuid4())
        now     = datetime.now(timezone.utc).isoformat()
        key     = f"case:{case_id}"
        await self._r.hset(key, mapping={
            "case_id":            case_id,
            "customer_id":        payload.customer_id,
            "transaction_id":     payload.transaction_id,
            "dispute_reason":     payload.dispute_reason,
            "dispute_amount_usd": str(payload.dispute_amount_usd),
            "status":             CaseStatus.PENDING,
            "risk_score":         "0.0",
            "risk_level":         "",
            "resolution_action":  "",
            "agent_rationale":    "",
            "created_at":         now,
            "updated_at":         now,
        })
        await self._r.expire(key, _CASE_TTL)
        await self._publish(case_id, {"status": CaseStatus.PENDING, "case_id": case_id})
        return case_id

    # ── Apply Agent Result ────────────────────────────────────────────
    async def apply_agent_result(self, result: AgentResult) -> None:
        key = f"case:{result.case_id}"
        now = datetime.now(timezone.utc).isoformat()
        await self._r.hset(key, mapping={
            "status":            result.resolution_action,
            "risk_score":        str(result.risk_score),
            "risk_level":        result.risk_level,
            "resolution_action": result.resolution_action,
            "agent_rationale":   result.agent_rationale,
            "updated_at":        now,
        })
        await self._publish(result.case_id, {
            "status":            result.resolution_action,
            "risk_score":        result.risk_score,
            "risk_level":        result.risk_level,
            "resolution_action": result.resolution_action,
            "agent_rationale":   result.agent_rationale,
        })

    # ── Apply Agent Error ─────────────────────────────────────────────
    async def apply_agent_error(self, error: AgentErrorResult) -> None:
        key = f"case:{error.case_id}"
        now = datetime.now(timezone.utc).isoformat()
        await self._r.hset(key, mapping={"status": "ERROR", "updated_at": now})
        await self._publish(error.case_id, {
            "status":       "ERROR",
            "error_code":   error.error_code,
            "error_detail": error.error_detail,
            "retryable":    error.retryable,
        })

    # ── SSE Streaming ─────────────────────────────────────────────────
    async def stream_case_events(
        self, case_id: str, customer_id: str
    ) -> AsyncIterator[dict]:
        """Yield Redis Stream events until terminal state or timeout."""
        case_key = f"case:{case_id}"
        owner    = await self._r.hget(case_key, "customer_id")
        if owner != customer_id:
            return  # silently close — ownership check, not an HTTP error

        stream_key      = f"stream:{case_id}"
        last_id         = "0"
        terminal_states = {"AUTO_APPROVE", "ANALYST_REVIEW", "RESOLVED", "CLOSED", "ERROR"}

        while True:
            entries = await self._r.xread({stream_key: last_id}, count=10, block=30_000)
            if not entries:
                continue
            for _, messages in entries:
                for msg_id, fields in messages:
                    last_id = msg_id
                    event   = json.loads(fields.get("data", "{}"))
                    yield event
                    if event.get("status") in terminal_states:
                        return

    # ── Publish Event ─────────────────────────────────────────────────
    async def publish_case_event(self, case_id: str, event: dict) -> None:
        await self._publish(case_id, event)

    # ── List Cases (analyst) ──────────────────────────────────────────
    async def list_cases(
        self, status_filter: str, page: int, page_size: int
    ) -> dict:
        from app.services.redis_client import DisputeCase
        cases = (
            DisputeCase.find(DisputeCase.status == status_filter)
            .sort_by("-created_at")
            .page(page, page_size)
        )
        total = len(DisputeCase.find(DisputeCase.status == status_filter).all())
        return {
            "cases":     [c.model_dump() for c in cases],
            "page":      page,
            "page_size": page_size,
            "total":     total,
        }

    # ── Internal ──────────────────────────────────────────────────────
    async def _publish(self, case_id: str, event: dict) -> None:
        stream_key = f"stream:{case_id}"
        await self._r.xadd(stream_key, {"data": json.dumps(event)})
        await self._r.expire(stream_key, _STREAM_TTL)