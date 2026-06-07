# backend/app/api/v1/disputes.py
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from fastapi.responses import StreamingResponse
from app.models.dispute import DisputeRequest, DisputeResponse
from app.services.orchestrator import run_dispute_pipeline
from app.services.session import SessionService
from app.services.redis_client import async_redis
from app.api.deps import get_verified_customer
import json, time

router = APIRouter()


@router.post(
    "/dispute",
    response_model=DisputeResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_dispute(
    payload: DisputeRequest,
    background_tasks: BackgroundTasks,
    customer_id: str = Depends(get_verified_customer),
) -> DisputeResponse:
    """
    Accepts a transaction dispute from the Customer Portal.
    Enqueues agent pipeline asynchronously; returns case_id immediately.
    Customer polls GET /dispute/{case_id}/status for updates.
    """
    # Ensure customer can only dispute their own transactions
    if payload.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot dispute transactions for a different account",
        )

    session = SessionService(async_redis)
    case_id = await session.create_case(payload)

    # Non-blocking: agent pipeline runs in background
    background_tasks.add_task(run_dispute_pipeline, payload, case_id)

    return DisputeResponse(
        case_id=case_id,
        status="PENDING",
        message="Dispute submitted. Processing initiated.",
    )


@router.get("/dispute/{case_id}/stream")
async def stream_case_status(
    case_id: str,
    customer_id: str = Depends(get_verified_customer),
) -> StreamingResponse:
    """
    Server-Sent Events stream for real-time case status updates.
    React frontend subscribes using EventSource API.
    """
    session = SessionService(async_redis)

    async def event_generator():
        async for event in session.stream_case_events(case_id, customer_id):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
