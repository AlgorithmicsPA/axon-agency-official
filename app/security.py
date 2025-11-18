import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, status
from app.core.types import Role, TokenPayload
from app.config import settings
from loguru import logger


def create_access_token(subject: str, role: Role) -> str:
    """Create a JWT access token."""
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=settings.jwt_expiration_hours)
    
    payload = {
        "sub": subject,
        "role": role.value,
        "iss": settings.jwt_iss,
        "aud": settings.jwt_aud,
        "exp": int(exp.timestamp()),
        "iat": int(now.timestamp()),
    }
    
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token


def decode_token(token: str) -> TokenPayload:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_aud,
            issuer=settings.jwt_iss,
        )
        
        return TokenPayload(
            sub=payload["sub"],
            role=Role(payload["role"]),
            iss=payload["iss"],
            aud=payload["aud"],
            exp=payload["exp"],
            iat=payload["iat"],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def verify_token(token: str) -> TokenPayload:
    """Verify token and return payload."""
    return decode_token(token)


def require_admin(token_payload: TokenPayload):
    """Require admin role."""
    if token_payload.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
