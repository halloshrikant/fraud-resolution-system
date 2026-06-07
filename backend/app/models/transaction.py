from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum


class TransactionStatus(str, Enum):
    APPROVED  = "APPROVED"
    DISPUTED  = "DISPUTED"
    REVERSED  = "REVERSED"
    PENDING   = "PENDING"


class TransactionRecord(BaseModel):
    customer_id:    str
    transaction_id: str
    merchant_name:  str
    amount_usd:     float = Field(gt=0.0)
    timestamp_utc:  str
    category:       str
    status:         TransactionStatus
    geolocation:    str

    @field_validator("customer_id", "transaction_id")
    @classmethod
    def alphanumeric_only(cls, v: str) -> str:
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        if not all(c in allowed for c in v):
            raise ValueError("ID contains invalid characters")
        return v


class TransactionListResponse(BaseModel):
    customer_id:  str
    transactions: list[TransactionRecord]
    total_count:  int
    date_from:    str
    date_to:      str


class TransactionSummary(BaseModel):
    """Lightweight summary passed between agents."""
    customer_id:       str
    total_spend_usd:   float
    transaction_count: int
    date_range_days:   int = 30
    top_merchants:     list[str] = Field(default_factory=list)
    anomaly_flags:     list[str] = Field(default_factory=list)