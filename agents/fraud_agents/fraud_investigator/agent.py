# agents/fraud_investigator/agent.py
from agents import Agent, function_tool
from fraud_agents.extensions.litellm import LiteLLMModel
from fraud_agents.shared.litellm_client import router
from fraud_agents.shared.pydantic_models import FraudResolutionResult, RiskLevel

_llm = LiteLLMModel(model_id="nova-lite", router=router)


fraud_investigator_agent = Agent(
    name="FraudInvestigatorAgent",
    model=_llm,
    instructions="""
    You are a senior fraud investigator AI. You receive:
    1. Applicable bank policy rules (from RAG Agent)
    2. Customer 30-day transaction analysis (from Transaction Analyst)
    3. The customer's original dispute claim

    Your task:
    - Assign a numeric risk_score between 0.0 (no fraud) and 1.0 (definite fraud)
    - Assign a risk_level: LOW (<0.35), MEDIUM (0.35-0.70), HIGH (>0.70)
    - Provide a detailed agent_rationale citing specific policy rules and transaction anomalies
    - Set resolution_action:
        * "AUTO_APPROVE" for risk_level == LOW
        * "ANALYST_REVIEW" for risk_level == MEDIUM or HIGH
    - List specific evidence_flags (e.g., "transaction 3hr after international purchase", "velocity >5 txn/hour")

    Produce ONLY a valid FraudResolutionResult JSON payload. No prose outside JSON.
    """,
    output_type=FraudResolutionResult,
)