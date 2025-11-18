"""Security utilities for JWT authentication and authorization."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import Settings, settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class TokenData(BaseModel):
    """JWT token payload data."""
    sub: str
    role: str
    iss: str
    aud: str
    exp: datetime


def validate_production_security(cfg: Settings):
    """Validate security configuration for production."""
    if cfg.production_mode:
        if cfg.jwt_secret == "change-me-in-production":
            logger.critical("CRITICAL: Using default JWT_SECRET in production mode!")
            raise RuntimeError("Cannot start with default JWT_SECRET in production")
        if cfg.dev_mode:
            logger.critical("CRITICAL: DEV_MODE enabled in production!")
            raise RuntimeError("Cannot start with DEV_MODE in production")
    else:
        if cfg.jwt_secret == "change-me-in-production":
            logger.warning("WARNING: Using default JWT_SECRET")
        if cfg.dev_mode:
            logger.warning("WARNING: DEV_MODE enabled")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(username: str, role: str = "viewer") -> str:
    """Create a JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiration_minutes)
    
    payload = {
        "sub": username,
        "role": role,
        "iss": settings.jwt_iss,
        "aud": settings.jwt_aud,
        "exp": expire
    }
    
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> TokenData:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            audience=settings.jwt_aud,
            issuer=settings.jwt_iss
        )
        return TokenData(**payload)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Dependency to get current authenticated user."""
    token = credentials.credentials
    return decode_token(token)


async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> TokenData:
    """Dependency to get current user, allowing dev mode bypass."""
    if settings.dev_mode and (credentials is None):
        # Dev mode: allow unauthenticated access for testing
        logger.warning("Dev mode: allowing unauthenticated request")
        return TokenData(
            sub="dev_user",
            role="admin",
            iss=settings.jwt_iss,
            aud=settings.jwt_aud,
            exp=datetime.now(timezone.utc) + timedelta(hours=24)
        )
    
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = credentials.credentials
    return decode_token(token)


async def require_admin(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Dependency to require admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    return current_user


def get_user_from_token(token_data: TokenData, session):
    """
    Helper function to get full User model from TokenData.
    Used internally by get_current_user_full.
    """
    from sqlmodel import select
    from app.models import User
    
    statement = select(User).where(User.username == token_data.sub)
    user = session.exec(statement).first()
    
    if not user:
        # DEV MODE: Allow dev token without DB user
        if settings.dev_mode and token_data.sub == "dev-admin":
            logger.warning(f"DEV MODE: Creating mock user for {token_data.sub}")
            # Return a mock User for dev mode
            from app.models.core import User as UserModel
            return UserModel(
                id=999,
                username="dev-admin",
                email="dev@example.com",
                hashed_password="",
                role="admin",
                tenant_id=None,
                is_active=True
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User {token_data.sub} not found in database"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user
