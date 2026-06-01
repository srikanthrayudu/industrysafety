import json
import time
import pytest

from app import app, sim


@pytest.fixture(autouse=True)
def start_sim():
    # ensure simulator is running for tests that need it
    sim.start()
    yield
    sim.stop()


def test_get_status(client=None):
    c = app.test_client()
    rv = c.get('/network/status')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'nodes' in data and 'links' in data and 'metrics' in data


def test_inject_and_restore():
    c = app.test_client()
    rv = c.post('/simulate/failure', json={'nodeId': 'B'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert any(n['id'] == 'B' and n['status'] == 'failed' for n in data['nodes'])

    rv2 = c.post('/simulate/restore', json={'nodeId': 'B'})
    assert rv2.status_code == 200
    data2 = rv2.get_json()
    assert any(n['id'] == 'B' and n['status'] == 'active' for n in data2['nodes'])


def test_metrics_history_and_mqtt_endpoints():
    c = app.test_client()
    # set mqtt mode on
    rv = c.post('/mqtt/mode', json={'enabled': True})
    assert rv.status_code == 200
    # publish a message
    rv2 = c.post('/mqtt/publish', json={'topic': 'test/topic', 'message': {'x': 1}})
    assert rv2.status_code == 200
    rv3 = c.get('/mqtt/messages?topic=test/topic&limit=10')
    assert rv3.status_code == 200
    data = rv3.get_json()
    assert data['topic'] == 'test/topic'

    # metrics history
    time.sleep(0.1)
    rv4 = c.get('/metrics/history?limit=5')
    assert rv4.status_code == 200
    hist = rv4.get_json()['history']
    assert isinstance(hist, list)

