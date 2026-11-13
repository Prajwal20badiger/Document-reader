from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_t01_health_endpoint():
    """T-01: Health endpoint returns healthy status and configuration without secrets."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "ocr_available" in data
    assert "ai_configured" in data
    assert "max_upload_size_mb" in data
    assert "allowed_extensions" in data
    assert ".pdf" in data["allowed_extensions"]

def test_t12_frontend_static_serving():
    """T-12: Frontend dist is served on root GET /"""
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Document Simplifier" in response.text
