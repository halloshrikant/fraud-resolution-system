# agents/fraud_investigator/tools.py
import json

from agents import function_tool
from fraud_agents.fraud_investigator.risk_scorer import compute_heuristic_score


@function_tool
def compute_heuristic_risk(
    transaction_analysis_json: str,
    dispute_amount_usd:        float,
) -> str:
    """
    Runs the rule-based pre-scorer on the transaction analysis JSON.
    Returns a baseline risk_score and triggered rule flags.
    The LLM agent uses this as evidence, not a final determination.
    """
    try:
        analysis = json.loads(transaction_analysis_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid transaction_analysis_json"})

    result = compute_heuristic_score(analysis, dispute_amount_usd)
    return json.dumps({
        "heuristic_score": result.score,
        "triggered_flags": result.flags,
    })