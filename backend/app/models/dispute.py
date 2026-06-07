# backend/app/models/dispute.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum


class CaseStatus(str, Enum):
    PENDING        = "PENDING"
    AUTO_APPROVED  = "AUTO_APPROVED"
    ANALYST_REVIEW = "ANALYST_REVIEW"
    IN_REVIEW      = "IN_REVIEW"
    RESOLVED       = "RESOLVED"
    CLOSED         = "CLOSED"
    ERROR          = "ERROR"


class DisputeRequest(BaseModel):
    customer_id:        str
    transaction_id:     str
    dispute_reason:     str   = Field(min_length=10, max_length=2000)
    dispute_amount_usd: float = Field(gt=0.0)

    @field_validator("customer_id", "transaction_id")
    @classmethod
    def alphanumeric_only(cls, v: str) -> str:
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        if not all(c in allowed for c in v):
            raise ValueError("ID contains invalid characters")
        return v


class DisputeResponse(BaseModel):
    case_id: str
    status:  CaseStatus
    message: str


class CaseStatusResponse(BaseModel):
    case_id:           str
    status:            CaseStatus
    risk_score:        Optional[float] = None
    risk_level:        Optional[str]   = None
    resolution_action: Optional[str]   = None
    agent_rationale:   Optional[str]   = None
    updated_at:        Optional[str]   = None


class CaseListResponse(BaseModel):
    cases:     list[CaseStatusResponse]
    page:      int
    page_size: int
    total:     int