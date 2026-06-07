# agents/rag_agent/retriever.py
import redis, struct, json
from redis.commands.search.query import Query
from ingestion.pipeline.embedder import embed_text
from app.config import settings


class PolicyRetriever:
    def __init__(self):
        self._r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_TLS_PORT,
            password=settings.REDIS_PASSWORD,
            ssl=True,
            decode_responses=False,
        )

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        embedding = embed_text(query)
        query_bytes = struct.pack(f"{len(embedding)}f", *embedding)

        # KNN vector similarity search using HNSW index
        q = (
            Query(f"(*)=>[KNN {top_k} @embedding $vec AS score]")
            .sort_by("score")
            .return_fields("doc_id", "policy_type", "chunk_text", "source_s3", "score")
            .dialect(2)
        )
        results = self._r.ft("policy_idx").search(q, query_params={"vec": query_bytes})

        return [
            {
                "doc_id":      doc.doc_id,
                "policy_type": doc.policy_type,
                "chunk_text":  doc.chunk_text,
                "source_s3":   doc.source_s3,
                "score":       float(doc.score),
            }
            for doc in results.docs
        ]