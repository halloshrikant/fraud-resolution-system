# agents/rag_agent/ingestion/pipeline.py
"""Wires S3 loader → Unstructured.io → Bedrock embedder → Redis indexer."""
from __future__ import annotations

import struct

import redis

from ingestion.pipeline.embedder            import embed_text
from ingestion.pipeline.unstructured_parser import stream_s3_documents
from ingestion.pipeline.redis_indexer       import create_policy_vector_index
from app.config import settings


def run_rag_ingestion(bucket: str) -> int:
    """One-shot ingestion of policy documents. Returns total chunks indexed."""
    r = redis.Redis(
        host             = settings.REDIS_HOST,
        port             = settings.REDIS_TLS_PORT,
        password         = settings.REDIS_PASSWORD,
        ssl              = True,
        decode_responses = False,
    )
    create_policy_vector_index(r)

    pipe       = r.pipeline(transaction=False)
    batch_size = 25
    count      = 0

    for chunk in stream_s3_documents(bucket):
        embedding = embed_text(chunk["chunk_text"])
        key       = f"policy:chunk:{chunk['doc_id']}:{chunk['chunk_index']}"
        pipe.json().set(key, "$", {
            "doc_id":      chunk["doc_id"],
            "policy_type": chunk["policy_type"],
            "chunk_text":  chunk["chunk_text"],
            "source_s3":   chunk["source_s3"],
            "embedding":   struct.pack(f"{len(embedding)}f", *embedding),
        })
        count += 1
        if count % batch_size == 0:
            pipe.execute()
            pipe = r.pipeline(transaction=False)
            print(f"Ingested {count} chunks...")

    pipe.execute()
    print(f"Ingestion complete. Total chunks: {count}")
    return count