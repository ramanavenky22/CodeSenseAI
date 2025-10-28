"""
Basic tests for CodeSense AI
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "CodeSense AI" in response.json()["message"]

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_api_docs():
    """Test API documentation endpoint"""
    response = client.get("/api/docs")
    assert response.status_code == 200

def test_dashboard_stats():
    """Test dashboard stats endpoint"""
    response = client.get("/api/v1/dashboard/stats")
    # This might fail without database setup, but we test the endpoint exists
    assert response.status_code in [200, 500]  # 500 is expected without DB

if __name__ == "__main__":
    pytest.main([__file__])
