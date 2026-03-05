"""
Web interface tests for background removal tool.
"""
import pytest
from fastapi.testclient import TestClient
from bg_removal.web import app

client = TestClient(app)

def test_root_endpoint():
    """Test that the root endpoint returns the web interface"""
    response = client.get("/")
    assert response.status_code == 200
    assert "背景移除工具" in response.text

def test_api_remove_bg_invalid_file_type():
    """Test API with invalid file type"""
    response = client.post(
        "/api/remove-bg",
        files={"file": ("test.txt", b"not an image", "text/plain")}
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

def test_api_remove_bg_file_too_large():
    """Test API with file larger than 10MB"""
    # Create a file larger than 10MB
    large_file = b"x" * (11 * 1024 * 1024)  # 11MB
    response = client.post(
        "/api/remove-bg",
        files={"file": ("large.jpg", large_file, "image/jpeg")}
    )
    assert response.status_code == 400
    assert "File size exceeds 10MB limit" in response.json()["detail"]