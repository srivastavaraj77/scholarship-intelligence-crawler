"""
Integration tests for FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.api.main import app
from app.database import init_db
from scripts.seed_data import seed_initial_database

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    init_db()
    seed_initial_database()


def test_api_metrics():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_discovered"] >= 20
    assert data["verified_count"] >= 10
    assert "avg_confidence" in data


def test_api_get_scholarships():
    response = client.get("/api/scholarships")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 20
    assert len(data["data"]) >= 20


def test_api_filter_by_source():
    response = client.get("/api/scholarships?source_type=Government - Central")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] > 0
    for s in data["data"]:
        assert s["source_type"] == "Government - Central"


def test_api_get_scholarship_detail():
    # Fetch list first to get a valid ID
    list_resp = client.get("/api/scholarships")
    first_id = list_resp.json()["data"][0]["id"]

    response = client.get(f"/api/scholarships/{first_id}")
    assert response.status_code == 200
    data = response.json()
    assert "scholarship" in data
    assert "history" in data
    assert data["scholarship"]["id"] == first_id
    assert "evidence_ledger" in data["scholarship"]


def test_api_simulate_change():
    response = client.post("/api/crawl/simulate-change")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["mutations"]) >= 2


def test_api_export_json_and_csv():
    json_resp = client.get("/api/export/json")
    assert json_resp.status_code == 200
    assert isinstance(json_resp.json(), list)

    csv_resp = client.get("/api/export/csv")
    assert csv_resp.status_code == 200
    assert "ID,Name,Provider" in csv_resp.text
