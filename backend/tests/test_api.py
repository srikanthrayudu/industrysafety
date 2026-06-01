from app import app


def test_get_status():
    client = app.test_client()
    response = client.get("/network/status")
    assert response.status_code == 200
    payload = response.get_json()
    assert "nodes" in payload
    assert "links" in payload
    assert "metrics" in payload


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
