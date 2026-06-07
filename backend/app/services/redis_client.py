# backend/app/services/redis_client.py
from redis.asyncio import Redis
from redis_om import get_redis_connection, JsonModel, Field
from app.config import settings

# Determine if SSL is enabled based on cert presence
use_ssl = bool(settings.REDIS_TLS_CERT and settings.REDIS_CA_CERT)

# Async client for FastAPI
async_redis: Redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_TLS_PORT,
    password=settings.REDIS_PASSWORD or None,
    ssl=use_ssl,
    ssl_certfile=settings.REDIS_TLS_CERT if use_ssl else None,
    ssl_keyfile=settings.REDIS_TLS_KEY if use_ssl else None,
    ssl_ca_certs=settings.REDIS_CA_CERT if use_ssl else None,
    decode_responses=True,
    max_connections=50,
)

# Synchronous client for Redis OM models
sync_redis = get_redis_connection(
    host=settings.REDIS_HOST,
    port=settings.REDIS_TLS_PORT,
    password=settings.REDIS_PASSWORD or None,
    ssl=use_ssl,
    ssl_certfile=settings.REDIS_TLS_CERT if use_ssl else None,
    ssl_keyfile=settings.REDIS_TLS_KEY if use_ssl else None,
    ssl_ca_certs=settings.REDIS_CA_CERT if use_ssl else None,
    decode_responses=True,
)


# ── Redis OM: Relational Model ────────────────────────────────────────────────
class TransactionRecord(JsonModel):
    """Stored as JSON in Redis; indexed for search."""
    customer_id: str = Field(index=True)
    transaction_id: str = Field(index=True)
    merchant_name: str = Field(index=True, full_text_search=True)
    amount_usd: float
    timestamp_utc: str = Field(index=True)
    category: str = Field(index=True)
    status: str = Field(index=True)   # APPROVED | DISPUTED | REVERSED
    geolocation: str

    class Meta:
        database = sync_redis
        global_key_prefix = "txn"
        encoding = "utf-8"


class DisputeCase(JsonModel):
    """Tracks the full lifecycle of a dispute case."""
    case_id:           str   = Field(index=True)
    customer_id:       str   = Field(index=True)
    transaction_id:    str   = Field(index=True)
    status:            str   = Field(index=True)
    risk_score:        float = Field(index=True, default=0.0)
    risk_level:        str   = Field(default="")
    resolution_action: str   = Field(default="")
    agent_rationale:   str   = Field(default="")
    assigned_analyst:  str   = Field(default="")
    resolved_by:       str   = Field(default="")
    created_at:        str   = Field(default="")
    updated_at:        str   = Field(default="")

    class Meta:
        database          = sync_redis
        global_key_prefix = "dispute"
        encoding = "utf-8"