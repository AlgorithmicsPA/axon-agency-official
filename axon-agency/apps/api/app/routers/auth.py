"""Authentication endpoints."""

import logging
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import get_session
from app.core.security import (
    create_access_token, verify_password, hash_password, get_current_user, TokenData
)
from app.models import User

logger = logging.getLogger(__name__)

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request payload."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    token_type: str = "bearer"
    user: dict


class RegisterRequest(BaseModel):
    """User registration request."""
    email: str
    username: str
    password: str
    full_name: str | None = None


@router.post("/dev/token")
async def dev_token():
    """Development-only endpoint to get an admin token."""
    if not settings.dev_mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not available in production mode"
        )
    
    logger.warning("DEV: Issuing development admin token")
    token = create_access_token("dev-admin", "admin")
    
    return TokenResponse(
        access_token=token,
        user={"username": "dev-admin", "role": "admin"}
    )


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, session: Session = Depends(get_session)):
    """Register a new user."""
    existing = session.exec(
        select(User).where(
            (User.email == request.email) | (User.username == request.username)
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    user = User(
        email=request.email,
        username=request.username,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
        role="viewer"
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    token = create_access_token(user.username, user.role)
    
    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, session: Session = Depends(get_session)):
    """Authenticate user and return JWT token."""
    user = session.exec(
        select(User).where(User.username == request.username)
    ).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    token = create_access_token(user.username, user.role)
    
    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    )


@router.get("/me")
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get current authenticated user info with tenant context."""
    from app.core.security import get_user_from_token
    from app.models.tenants import Tenant
    
    # Get full User model from database
    user = get_user_from_token(current_user, session)
    
    # Build response with tenant info if user has tenant_id
    response = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_admin": user.role == "admin",
        "tenant_id": user.tenant_id,
        "tenant_slug": None,
        "tenant_name": None
    }
    
    # If user belongs to a tenant, fetch tenant details
    if user.tenant_id:
        tenant = session.get(Tenant, user.tenant_id)
        if tenant:
            response["tenant_slug"] = tenant.slug
            response["tenant_name"] = tenant.name
    
    return response
