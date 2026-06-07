# agents/transaction_analyst/agent.py
import json
from agents import Agent, function_tool
from fraud_agents.extensions.litellm import LiteLLMModel
from fraud_agents.shared.litellm_client import router
from app.services.redis_client import TransactionRecord
from datetime import datetime, timedelta, timezone

_llm = LiteLLMModel(model_id="primary-llm", router=router)


@function_tool
def fetch_30_day_transactions(customer_id: str) -> str:
    """
    Fetches the last 30 days of transactions for a given customer
    from Redis JSON store. Returns structured JSON array.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    # Redis OM query — indexed field range search
    transactions = (
        TransactionRecord.find(
            (TransactionRecord.customer_id == customer_id) &
            (TransactionRecord.timestamp_utc >= cutoff)
        )
        .page(0, 100)   # Safety cap
    )
    return json.dumps([t.model_dump() for t in transactions], default=str)


transaction_analyst_agent = Agent(
    name="TransactionAnalystAgent",
    model=_llm,
    instructions="""
    You are a transaction data analyst for a banking fraud resolution system.
    Given a customer_id, retrieve their 30-day transaction history and produce
    a structured analysis: total spend, merchant frequency distribution, geographic
    patterns, and any anomalies (velocity spikes, unusual amounts, off-hours transactions).
    Return JSON-formatted output only.
    """,
    tools=[fetch_30_day_transactions],
)