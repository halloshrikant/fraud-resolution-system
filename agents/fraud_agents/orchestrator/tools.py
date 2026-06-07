# agents/orchestrator/tools.py
from agents import function_tool


@function_tool
def summarise_pipeline_result(
    policy_summary:       str,
    transaction_analysis: str,
    fraud_assessment:     str,
) -> str:
    """
    Combines outputs from all three specialist agents into a single
    cohesive audit-trail summary stored with the dispute case.
    """
    return (
        f"=== Policy Rules ===\n{policy_summary}\n\n"
        f"=== Transaction Analysis ===\n{transaction_analysis}\n\n"
        f"=== Fraud Assessment ===\n{fraud_assessment}"
    )