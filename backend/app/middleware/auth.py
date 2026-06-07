# backend/app/middleware/auth.py
"""
Defense-in-depth JWT middleware.
Excludes /health and /ready from auth; per-endpoint deps.py handles fine-grained checks.
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.deps import _verify_token
from app.config import settings

_PUBLIC = {"/health", "/ready"}


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip auth in dev mode
        if settings.DEV_MODE:
            return await call_next(request)
        
        if request.url.path in _PUBLIC:
            return await call_next(request)

        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing Authorization header"})

        try:
            _verify_token(auth.removeprefix("Bearer ").strip())
        except Exception:
            return JSONResponse(status_code=401, content={"detail": "Token validation failed"})

        return await call_next(request)