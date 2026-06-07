# ingestion/pipeline/redis_indexer.py
import redis
from redis.commands.search.field import VectorField, TagField, TextField
from redis.commands.search.index_definition import IndexDefinition, IndexType

def create_policy_vector_index(r: redis.Redis) -> None:
    """
    Creates a Redis HNSW index for semantic policy search.
    Embedding dim=1536 matches Amazon Titan Embed Text v2.
    """
    schema = (
        TagField("$.doc_id",       as_name="doc_id"),
        TagField("$.policy_type",  as_name="policy_type"),
        TextField("$.chunk_text",  as_name="chunk_text"),
        VectorField(
            "$.embedding",
            "HNSW",
            {
                "TYPE":            "FLOAT32",
                "DIM":             1536,
                "DISTANCE_METRIC": "COSINE",
                "M":               16,
                "EF_CONSTRUCTION": 200,
                "EF_RUNTIME":      10,
            },
            as_name="embedding",
        ),
    )
    definition = IndexDefinition(
        prefix=["policy:chunk:"],
        index_type=IndexType.JSON,
    )
    try:
        r.ft("policy_idx").create_index(schema, definition=definition)
    except redis.exceptions.ResponseError as e:
        if "Index already exists" not in str(e):
            raise
