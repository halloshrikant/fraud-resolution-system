# backend/app/middleware/logging.py
"""
Structured JSON request logging — one line per request.
PII fields (Authorization, cookie) are never logged.
"""
import json
import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("fraud_api")


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        start      = time.monotonic()
        response   = await call_next(request)
        logger.info(json.dumps({
            "request_id":  request_id,
            "method":      request.method,
            "path":        request.url.path,
            "status_code": response.status_code,
            "duration_ms": round((time.monotonic() - start) * 1000, 2),
            "client_ip":   request.client.host if request.client else None,
        }))
        response.headers["X-Request-ID"] = request_id
        return response