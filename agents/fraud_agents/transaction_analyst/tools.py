# agents/transaction_analyst/tools.py
import json
from datetime import datetime, timedelta, timezone

from agents import function_tool


@function_tool
def get_transaction_velocity(customer_id: str, hours: int = 24) -> str:
    """
    Counts transactions and total spend in the last N hours.
    Used to detect velocity spikes indicating card compromise.
    """
    from app.services.redis_client import TransactionRecord
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    txns   = TransactionRecord.find(
        (TransactionRecord.customer_id == customer_id) &
        (TransactionRecord.timestamp_utc >= cutoff)
    ).all()
    return json.dumps({
        "customer_id":       customer_id,
        "window_hours":      hours,
        "transaction_count": len(txns),
        "total_spend_usd":   round(sum(t.amount_usd for t in txns), 2),
    })


@function_tool
def get_merchant_frequency(customer_id: str) -> str:
    """
    Returns per-merchant transaction counts over the last 30 days.
    Useful for detecting first-time merchants during fraud review.
    """
    from app.services.redis_client import TransactionRecord
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    txns   = TransactionRecord.find(
        (TransactionRecord.customer_id == customer_id) &
        (TransactionRecord.timestamp_utc >= cutoff)
    ).all()
    freq: dict[str, int] = {}
    for t in txns:
        freq[t.merchant_name] = freq.get(t.merchant_name, 0) + 1
    return json.dumps({"customer_id": customer_id, "merchant_frequency": freq})