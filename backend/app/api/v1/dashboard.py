# backend/app/api/v1/dashboard.py
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_verified_analyst
from app.services.redis_client import DisputeCase, async_redis
from app.services.session import SessionService

router = APIRouter()


# ── List Cases ────────────────────────────────────────────────────────
@router.get("/cases")
async def get_cases(
    status_filter: str = Query(default="ANALYST_REVIEW"),
    page:          int = Query(default=0, ge=0),
    page_size:     int = Query(default=20, ge=1, le=100),
    analyst_id:    str = Depends(get_verified_analyst),
) -> dict:
    """Returns paginated cases for the analyst review queue."""
    cases = (
        DisputeCase.find(DisputeCase.status == status_filter)
        .sort_by("-created_at")
        .page(page, page_size)
    )
    return {"cases": [c.model_dump() for c in cases], "page": page, "page_size": page_size}


# ── Get Single Case ───────────────────────────────────────────────────
@router.get("/cases/{case_id}")
async def get_case_detail(
    case_id:    str,
    analyst_id: str = Depends(get_verified_analyst),
) -> dict:
    results = DisputeCase.find(DisputeCase.case_id == case_id).page(0, 1)
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return results[0].model_dump()


# ── Assign Case ───────────────────────────────────────────────────────
@router.post("/cases/{case_id}/assign")
async def assign_case(
    case_id:    str,
    analyst_id: str = Depends(get_verified_analyst),
) -> dict:
    results = DisputeCase.find(DisputeCase.case_id == case_id).page(0, 1)
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    case                  = results[0]
    case.assigned_analyst = analyst_id
    case.status           = "IN_REVIEW"
    case.updated_at       = datetime.now(timezone.utc).isoformat()
    case.save()
    return {"message": "Case assigned", "case_id": case_id, "analyst_id": analyst_id}


# ── Approve Refund ────────────────────────────────────────────────────
@router.post("/cases/{case_id}/approve")
async def approve_case(
    case_id:    str,
    analyst_id: str = Depends(get_verified_analyst),
) -> dict:
    results = DisputeCase.find(DisputeCase.case_id == case_id).page(0, 1)
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    case                   = results[0]
    case.status            = "RESOLVED"
    case.resolution_action = "APPROVED"
    case.resolved_by       = analyst_id
    case.updated_at        = datetime.now(timezone.utc).isoformat()
    case.save()

    await SessionService(async_redis).publish_case_event(
        case_id = case.case_id,
        event   = {"status": "RESOLVED", "resolution_action": "APPROVED", "updated_by": analyst_id},
    )
    return {"message": "Refund approved", "case_id": case_id}


# ── Deny Claim ────────────────────────────────────────────────────────
@router.post("/cases/{case_id}/deny")
async def deny_case(
    case_id:    str,
    analyst_id: str = Depends(get_verified_analyst),
) -> dict:
    results = DisputeCase.find(DisputeCase.case_id == case_id).page(0, 1)
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    case                   = results[0]
    case.status            = "CLOSED"
    case.resolution_action = "DENIED"
    case.resolved_by       = analyst_id
    case.updated_at        = datetime.now(timezone.utc).isoformat()
    case.save()

    await SessionService(async_redis).publish_case_event(
        case_id = case.case_id,
        event   = {"status": "CLOSED", "resolution_action": "DENIED", "updated_by": analyst_id},
    )
    return {"message": "Claim denied", "case_id": case_id}


# ── Dashboard Metrics ─────────────────────────────────────────────────
@router.get("/dashboard/metrics")
async def get_dashboard_metrics(
    analyst_id: str = Depends(get_verified_analyst),
) -> dict:
    """Analyst dashboard KPIs — counts per status."""
    return {
        "pending":        len(DisputeCase.find(DisputeCase.status == "PENDING").all()),
        "analyst_review": len(DisputeCase.find(DisputeCase.status == "ANALYST_REVIEW").all()),
        "in_review":      len(DisputeCase.find(DisputeCase.status == "IN_REVIEW").all()),
        "resolved":       len(DisputeCase.find(DisputeCase.status == "RESOLVED").all()),
        "generated_at":   datetime.now(timezone.utc).isoformat(),
    }