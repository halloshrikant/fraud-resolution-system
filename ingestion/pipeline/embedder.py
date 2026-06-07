# ingestion/pipeline/embedder.py
import boto3
import json
from typing import List

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def embed_text(text: str) -> List[float]:
    """
    Amazon Titan Embed Text v2 — 1536-dim embeddings.
    Normalized for cosine similarity.
    """
    body = json.dumps({
        "inputText":    text,
        "dimensions":   1536,
        "normalize":    True,
    })
    response = bedrock.invoke_model(
        modelId    = "amazon.titan-embed-text-v2:0",
        body       = body,
        contentType= "application/json",
        accept     = "application/json",
    )
    return json.loads(response["body"].read())["embedding"]
