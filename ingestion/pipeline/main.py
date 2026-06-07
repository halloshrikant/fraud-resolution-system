import redis
import json
import struct
from ingestion.pipeline.embedder           import embed_text
from ingestion.pipeline.unstructured_parser import stream_s3_documents
from ingestion.pipeline.redis_indexer       import create_policy_vector_index
from app.config import settings

def run_ingestion_pipeline(bucket: str) -> None:
    r = redis.Redis(
        host             = settings.REDIS_HOST,
        port             = settings.REDIS_TLS_PORT,
        password         = settings.REDIS_PASSWORD,
        ssl              = True,
        decode_responses = False,
    )
    create_policy_vector_index(r)
    pipe              = r.pipeline(transaction=False)
    batch_size, count = 25, 0

    for chunk in stream_s3_documents(bucket):
        embedding = embed_text(chunk["chunk_text"])
        key       = f"policy:chunk:{chunk['doc_id']}:{chunk['chunk_index']}"
        payload   = {
            "doc_id":      chunk["doc_id"],
            "policy_type": chunk["policy_type"],
            "chunk_text":  chunk["chunk_text"],
            "source_s3":   chunk["source_s3"],
            "embedding":   struct.pack(f"{len(embedding)}f", *embedding),
        }
        pipe.json().set(key, "$", payload)
        count += 1
        if count % batch_size == 0:
            pipe.execute()
            pipe = r.pipeline(transaction=False)
            print(f"Ingested {count} chunks...")

    pipe.execute()
    print(f"Ingestion complete. Total chunks: {count}")