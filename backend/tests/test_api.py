from app import app


def test_get_status():
    client = app.test_client()
    response = client.get("/network/status")
    assert response.status_code == 200
    payload = response.get_json()
    assert "nodes" in payload
    assert "links" in payload
    assert "metrics" in payload
    assert "safety" in payload
    assert "thresholds" in payload
    assert all("protocol" in link for link in payload["links"])


def test_fail_restore_node():
    client = app.test_client()

    fail_response = client.post("/simulate/failure", json={"nodeId": "B"})
    assert fail_response.status_code == 200
    fail_payload = fail_response.get_json()
    assert any(node["id"] == "B" and node["status"] == "failed" for node in fail_payload["nodes"])

    restore_response = client.post("/simulate/restore", json={"nodeId": "B"})
    assert restore_response.status_code == 200
    restore_payload = restore_response.get_json()
    assert any(node["id"] == "B" and node["status"] == "active" for node in restore_payload["nodes"])


def test_random_probability_and_logs():
    client = app.test_client()

    random_response = client.post("/simulate/random", json={"probability": 0.2})
    assert random_response.status_code == 200
    assert random_response.get_json()["probability"] == 0.2

    logs_response = client.get("/logs?limit=10")
    assert logs_response.status_code == 200
    logs = logs_response.get_json()["logs"]
    assert isinstance(logs, list)


def test_api_simulate_safety_events():
    client = app.test_client()
    client.post("/api/reset")

    dos_response = client.post("/api/simulate", json={"event": "dos", "durationTicks": 3})
    assert dos_response.status_code == 200
    assert dos_response.get_json()["scenario"]["dosActive"] is True

    esd_response = client.post("/api/simulate", json={"event": "esd_failure"})
    assert esd_response.status_code == 200
    payload = esd_response.get_json()
    assert payload["metrics"]["esdFailures"] == 1

    reset_response = client.post("/api/simulate", json={"event": "reset_conditions"})
    assert reset_response.status_code == 200
    assert reset_response.get_json()["scenario"]["dosActive"] is False


def test_safety_status_reports_threshold_violations():
    client = app.test_client()
    client.post("/api/reset")

    response = client.post("/api/simulate", json={"event": "latency", "latencyMs": 200})
    assert response.status_code == 200
    payload = response.get_json()

    assert payload["thresholds"]["maxDelayMs"] == 150.0
    assert payload["safety"]["level"] in {"normal", "degraded", "critical"}
