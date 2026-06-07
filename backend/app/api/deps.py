# backend/app/api/deps.py
"""JWT validation via AWS Cognito JWKS."""
from __future__ import annotations

import httpx
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwk, jwt
from typing import Optional

from app.config import settings

_bearer = HTTPBearer(auto_error=False)  # Don't auto-raise on missing header


@lru_cache(maxsize=1)
def _fetch_jwks() -> dict:
    """Download Cognito JWKS once and cache for process lifetime."""
    url  = (
        f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/"
        f"{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    )
    resp = httpx.get(url, timeout=5)
    resp.raise_for_status()
    return {k["kid"]: k for k in resp.json()["keys"]}


def _verify_token(token: str) -> dict:
    try:
        header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token header")

    jwks = _fetch_jwks()
    if header["kid"] not in jwks:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown signing key")

    public_key = jwk.construct(jwks[header["kid"]])
    issuer     = (
        f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/"
        f"{settings.COGNITO_USER_POOL_ID}"
    )
    try:
        claims = jwt.decode(
            token,
            public_key,
            algorithms  = ["RS256"],
            audience    = settings.COGNITO_CLIENT_ID,
            issuer      = issuer,
        )
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    return claims


async def get_verified_customer(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> str:
    """Returns the authenticated customer_id from the JWT 'sub' claim."""
    # Dev mode bypass
    if settings.DEV_MODE:
        return "dev-customer-123"
    
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization")
    
    claims      = _verify_token(credentials.credentials)
    customer_id = claims.get("sub") or claims.get("username")
    if not customer_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing subject claim")
    return customer_id


async def get_verified_analyst(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> str:
    """Returns analyst_id; also validates 'analysts' Cognito group membership."""
    # Dev mode bypass
    if settings.DEV_MODE:
        return "dev-analyst-456"
    
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization")
    
    claims = _verify_token(credentials.credentials)
    if "analysts" not in claims.get("cognito:groups", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Analyst role required")
    return claims.get("sub") or claims.get("username")