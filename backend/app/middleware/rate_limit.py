# backend/app/middleware/rate_limit.py
"""
Fixed-window token-bucket rate limiter backed by Redis.
Default: 100 requests / 60-second window per identity.
Identity = SHA-256(token) prefix if authed, else client IP.
"""
import hashlib
import time

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.redis_client import async_redis


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.max_requests   = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next) -> Response:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            identifier = hashlib.sha256(auth[7:].encode()).hexdigest()[:16]
        else:
            identifier = request.client.host if request.client else "unknown"

        window     = int(time.time()) // self.window_seconds
        bucket_key = f"ratelimit:{identifier}:{window}"
        count      = await async_redis.incr(bucket_key)
        if count == 1:
            await async_redis.expire(bucket_key, self.window_seconds * 2)

        if count > self.max_requests:
            return JSONResponse(
                status_code = 429,
                content     = {"detail": "Rate limit exceeded. Retry after 60 seconds."},
                headers     = {"Retry-After": str(self.window_seconds)},
            )
        return await call_next(request)