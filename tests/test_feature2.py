import pytest
from app import create_app
from app.features.feature2.standalone import create_standalone_app


@pytest.fixture
def client():
    """Create test client with Feature 2 enabled."""
    app = create_app("testing")
    with app.test_client() as client:
        yield client


@pytest.fixture
def standalone_client():
    """Create test client for Feature 2 standalone mode."""
    app = create_standalone_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_feature2_page_loads(client):
    """Verify that Feature 2 page renders with 200 OK."""
    response = client.get("/feature2/")
    assert response.status_code == 200
    assert b"Feature 2: System Diagnostics & Health" in response.data
    assert b"Live Host &amp; Runtime Metrics" in response.data or b"Live Host & Runtime Metrics" in response.data


def test_feature2_diagnostics_api(client):
    """Verify that diagnostics API returns operational status and telemetry."""
    response = client.get("/feature2/api/diagnostics")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "operational"
    assert "process" in data
    assert "host" in data
    assert "uptime_seconds" in data["process"]
    assert "hostname" in data["host"]


def test_feature2_standalone_mode(standalone_client):
    """Verify that Feature 2 can execute independently in standalone microserver mode."""
    # Test root redirect
    redirect_resp = standalone_client.get("/")
    assert redirect_resp.status_code == 302
    assert "/feature2" in redirect_resp.headers["Location"]

    # Test health check
    health_resp = standalone_client.get("/feature2/api/health")
    assert health_resp.status_code == 200
    assert health_resp.get_json()["status"] == "healthy"
