# fraud_agents/shared/mlflow_tracker.py
import mlflow
import os
import time
from typing import Any

# Use local SQLite for dev, Kubernetes service for production
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"))


class MLflowSpanTracker:
    """
    Logs full agent execution metadata to MLflow.
    Each dispute invocation = 1 MLflow Run with nested spans.
    """
    def __init__(self, case_id: str):
        self.case_id   = case_id
        self.run       = None
        self._start_ms = time.monotonic() * 1000

    def __enter__(self):
        mlflow.set_experiment("fraud-resolution-agents")
        self.run = mlflow.start_run(run_name=f"dispute-{self.case_id}")
        mlflow.set_tags({
            "case_id":       self.case_id,
            "agent_version": "1.0.0",
            "env":           "production",
        })
        return self

    def log_agent_step(self, agent_name: str, prompt: str, response: str, tokens: dict) -> None:
        with mlflow.start_span(name=agent_name) as span:
            span.set_inputs({"prompt": prompt[:4000]})    # Truncate for storage limits
            span.set_outputs({"response": response[:4000]})
            mlflow.log_metrics({
                f"{agent_name}.prompt_tokens":     tokens.get("prompt_tokens", 0),
                f"{agent_name}.completion_tokens": tokens.get("completion_tokens", 0),
                f"{agent_name}.total_tokens":      tokens.get("total_tokens", 0),
            })

    def log_agent_run(self, result: Any) -> None:
        elapsed_ms = (time.monotonic() * 1000) - self._start_ms
        # Handle both direct result objects and wrapped results with final_output
        if hasattr(result, 'final_output'):
            result_obj = result.final_output
        else:
            result_obj = result
            
        mlflow.log_metrics({
            "total_pipeline_latency_ms": elapsed_ms,
            "risk_score":               result_obj.risk_score,
        })
        mlflow.log_param("resolution_action", result_obj.resolution_action)
        mlflow.log_param("risk_level",        result_obj.risk_level)

    def __exit__(self, *args):
        mlflow.end_run()