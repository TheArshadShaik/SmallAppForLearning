import pytest
from app import create_app


@pytest.fixture
def client():
    """Create test client using testing configuration."""
    app = create_app("testing")
    with app.test_client() as client:
        yield client


def test_home_page_status(client):
    """Verify that home page loads with 200 OK."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"SmallApp" in response.data
    assert b"Home Gateway" in response.data


def test_health_check_endpoint(client):
    """Verify health endpoint returns status healthy and JSON payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "hostname" in data
    assert "version" in data


def test_api_info_endpoint(client):
    """Verify API info endpoint returns application metadata."""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.get_json()
    assert "app_name" in data
    assert "blueprints" in data
    assert "main" in data["blueprints"]


def test_404_error_page(client):
    """Verify custom 404 page for nonexistent routes."""
    response = client.get("/nonexistent-page-test-xyz")
    assert response.status_code == 404
    assert b"404" in response.data
    assert b"Page Not Found" in response.data
