from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "running"


def test_scan_and_incidents_flow():
    # Trigger a scan; this will populate the in-memory incident store.
    resp = client.post("/scan")
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Scan completed"
    assert "incidents_found" in data
    assert "scan_timestamp" in data

    # Metrics endpoint should always return the full metrics schema.
    metrics_resp = client.get("/metrics")
    assert metrics_resp.status_code == 200
    metrics = metrics_resp.json()
    for key in ["total", "critical", "high", "medium", "low"]:
        assert key in metrics

    # Incidents table view must be a list and must not contain raw_text.
    incidents_resp = client.get("/incidents")
    assert incidents_resp.status_code == 200
    incidents = incidents_resp.json()
    assert isinstance(incidents, list)
    if incidents:
        sample = incidents[0]
        assert "incident_id" in sample
        assert "source" in sample
        assert "timestamp" in sample
        assert "severity" in sample
        assert "risk_score" in sample
        assert "entity_count" in sample
        # Table view should not include raw_text or entities.
        assert "raw_text" not in sample
        assert "entities" not in sample

        # Detail view for a single incident
        detail_resp = client.get(f"/incidents/{sample['incident_id']}")
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        for key in [
            "incident_id",
            "source",
            "url",
            "timestamp",
            "severity",
            "risk_score",
            "entities",
            "context_snippet",
        ]:
            assert key in detail


