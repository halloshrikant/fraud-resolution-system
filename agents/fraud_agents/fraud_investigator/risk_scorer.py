# agents/fraud_investigator/risk_scorer.py
"""
Heuristic pre-scorer applied before LLM assessment.
Returns a float in [0.0, 0.9] and triggered rule flags.
The LLM agent makes the final determination.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class HeuristicScore:
    score: float
    flags: list[str] = field(default_factory=list)


def compute_heuristic_score(
    transaction_analysis: dict,
    dispute_amount_usd:   float,
) -> HeuristicScore:
    score: float    = 0.0
    flags: list[str] = []

    total_spend       = transaction_analysis.get("total_spend_usd", 0.0)
    transaction_count = transaction_analysis.get("transaction_count", 0)
    anomaly_flags     = transaction_analysis.get("anomaly_flags", [])

    if total_spend > 0 and dispute_amount_usd / total_spend > 0.5:
        score += 0.25
        flags.append(f"Dispute is {dispute_amount_usd / total_spend:.0%} of 30-day spend")

    if transaction_count > 20:
        score += 0.15
        flags.append(f"High velocity: {transaction_count} transactions in 30 days")

    for anomaly in anomaly_flags:
        score += 0.10
        flags.append(anomaly)

    return HeuristicScore(score=min(round(score, 3), 0.9), flags=flags)