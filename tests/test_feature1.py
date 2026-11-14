import pytest
from app import create_app
from app.features.feature1.standalone import create_standalone_app


@pytest.fixture
def client():
    """Create client with Feature 1 enabled."""
    app = create_app("testing")
    with app.test_client() as client:
        yield client


@pytest.fixture
def standalone_client():
    """Create test client for Feature 1 running in standalone microserver mode."""
    standalone_app = create_standalone_app()
    standalone_app.config["TESTING"] = True
    with standalone_app.test_client() as client:
        yield client


def test_feature1_page_loads(client):
    """Test Feature 1 HTML page rendering."""
    response = client.get("/feature1/")
    assert response.status_code == 200
    assert b"Feature 1: Capacity & Cost Estimator" in response.data
    assert b"Cloud EC2 Compute Cost Calculator" in response.data


def test_feature1_calculate_success(client):
    """Test API calculate endpoint with valid payload."""
    payload = {
        "instances": 3,
        "hours": 10,
        "rate": 0.05
    }
    response = client.post("/feature1/api/calculate", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["calculation"]["total_cost_usd"] == 1.50
    assert data["calculation"]["total_compute_hours"] == 30


def test_feature1_calculate_invalid_data(client):
    """Test API calculate endpoint rejects negative numbers."""
    payload = {
        "instances": -1,
        "hours": 10,
        "rate": 0.05
    }
    response = client.post("/feature1/api/calculate", json=payload)
    assert response.status_code == 422
    data = response.get_json()
    assert "error" in data


def test_feature1_calculate_missing_body(client):
    """Test API calculate endpoint rejects empty request."""
    response = client.post("/feature1/api/calculate", data="not json", content_type="text/plain")
    assert response.status_code == 400


def test_feature1_standalone_mode(standalone_client):
    """Test that Feature 1 can run as a standalone microserver."""
    # Test root redirect in standalone
    redirect_resp = standalone_client.get("/")
    assert redirect_resp.status_code == 302
    assert "/feature1" in redirect_resp.headers["Location"]
    
    # Test health check in standalone
    health_resp = standalone_client.get("/feature1/api/health")
    assert health_resp.status_code == 200
    assert health_resp.get_json()["status"] == "healthy"
