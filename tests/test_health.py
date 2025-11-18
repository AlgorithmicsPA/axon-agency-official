import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "message" in data


def test_dev_token_endpoint():
    """Test dev token generation (only available in DEV_MODE)."""
    from app.config import settings
    
    if settings.dev_mode:
        response = client.post("/api/token/dev?username=test-user")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "admin"
