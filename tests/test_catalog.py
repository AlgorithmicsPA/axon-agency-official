import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.security import create_access_token
from app.core.types import Role


client = TestClient(app)


def test_catalog_requires_auth():
    """Test catalog endpoint requires authentication."""
    response = client.get("/api/catalog")
    assert response.status_code == 403


def test_catalog_with_auth():
    """Test catalog endpoint with valid token."""
    token = create_access_token("test-user", Role.VIEWER)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/catalog", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "version" in data
    assert "dev_mode" in data
    assert "audit_loaded" in data
    assert "services_detected" in data
    assert "capabilities" in data


def test_catalog_structure():
    """Test catalog response structure."""
    token = create_access_token("test-user", Role.ADMIN)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/catalog", headers=headers)
    data = response.json()
    
    assert isinstance(data["services_detected"], dict)
    assert isinstance(data["capabilities"], dict)
