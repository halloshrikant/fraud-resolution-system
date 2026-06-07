# agents/shared/litellm_client.py
from litellm import Router

# LiteLLM acts as a unified interface between OpenAI SDK and Bedrock
router = Router(
    model_list=[
        {
            "model_name":  "nova-lite",   # Logical name used by agents
            "litellm_params": {
                "model":        "bedrock/amazon.nova-lite-v1:0",
                "aws_region_name": "us-east-1",
                # IRSA — no static keys; boto3 uses pod's IAM role
            },
        },
        {
            # Fallback to Claude Haiku if Nova-Lite quota exceeded
            "model_name":  "claude-haiku",
            "litellm_params": {
                "model":        "bedrock/anthropic.claude-3-haiku-20240307-v1:0",
                "aws_region_name": "us-east-1",
            },
        },
    ],
    fallbacks=[{"nova-lite": ["claude-haiku"]}],
    num_retries=3,
    retry_after=2,
    allowed_fails=2,
    routing_strategy="least-busy",
    set_verbose=False,
)