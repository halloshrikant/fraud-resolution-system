# agents/shared/pydantic_models.py
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import Optional
import uuid


class RiskLevel(str, Enum):
    LOW    = "LOW"
    MEDIUM = "MEDIUM"
    HIGH   = "HIGH"


class ResolutionAction(str, Enum):
    AUTO_APPROVE    = "AUTO_APPROVE"
    ANALYST_REVIEW  = "ANALYST_REVIEW"


class DisputeRequest(BaseModel):
    case_id:           str          = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id:       str
    transaction_id:    str
    dispute_reason:    str          = Field(min_length=10, max_length=2000)
    dispute_amount_usd: float       = Field(gt=0.0)

    @field_validator("customer_id", "transaction_id")
    @classmethod
    def no_injection(cls, v: str) -> str:
        # Guard against Redis key injection / prompt injection via IDs
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        if not all(c in allowed for c in v):
            raise ValueError("ID contains invalid characters")
        return v


class FraudResolutionResult(BaseModel):
    case_id:           str
    risk_score:        float            = Field(ge=0.0, le=1.0)
    risk_level:        RiskLevel
    resolution_action: ResolutionAction
    agent_rationale:   str
    evidence_flags:    list[str]        = Field(default_factory=list)
    applicable_policies: list[str]     = Field(default_factory=list)
    processing_time_ms: Optional[float] = None