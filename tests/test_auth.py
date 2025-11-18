import pytest
from app.security import create_access_token, decode_token, verify_token
from app.core.types import Role
from fastapi import HTTPException


def test_create_and_decode_token():
    """Test JWT token creation and decoding."""
    token = create_access_token("test-user", Role.ADMIN)
    assert isinstance(token, str)
    assert len(token) > 0
    
    payload = decode_token(token)
    assert payload.sub == "test-user"
    assert payload.role == Role.ADMIN


def test_verify_token():
    """Test token verification."""
    token = create_access_token("viewer-user", Role.VIEWER)
    payload = verify_token(token)
    assert payload.sub == "viewer-user"
    assert payload.role == Role.VIEWER


def test_invalid_token():
    """Test invalid token raises exception."""
    with pytest.raises(HTTPException):
        decode_token("invalid-token-string")
