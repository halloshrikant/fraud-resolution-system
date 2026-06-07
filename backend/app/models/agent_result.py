from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class RiskLevel(str, Enum):
    LOW    = "LOW"
    MEDIUM = "MEDIUM"
    HIGH   = "HIGH"


class ResolutionAction(str, Enum):
    AUTO_APPROVE   = "AUTO_APPROVE"
    ANALYST_REVIEW = "ANALYST_REVIEW"


class AgentStepLog(BaseModel):
    """Captures a single agent's execution step for audit trail."""
    agent_name:        str
    input_summary:     str
    output_summary:    str
    prompt_tokens:     int   = 0
    completion_tokens: int   = 0
    latency_ms:        float = 0.0


class AgentResult(BaseModel):
    """
    The full structured result returned by the fraud pipeline.
    Stored in Redis and surfaced to the Analyst Dashboard.
    """
    case_id:              str
    risk_score:           float            = Field(ge=0.0, le=1.0)
    risk_level:           RiskLevel
    resolution_action:    ResolutionAction
    agent_rationale:      str
    evidence_flags:       list[str]        = Field(default_factory=list)
    applicable_policies:  list[str]        = Field(default_factory=list)
    agent_steps:          list[AgentStepLog] = Field(default_factory=list)
    processing_time_ms:   Optional[float]  = None
    model_used:           Optional[str]    = None


class AgentErrorResult(BaseModel):
    """Returned when the agent pipeline fails — prevents silent data loss."""
    case_id:      str
    error_code:   str
    error_detail: str
    retryable:    bool = True