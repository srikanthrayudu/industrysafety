# Industrial Communication Reliability Simulator (backend)

This backend provides a minimal Flask API and a simple in-memory simulator for the Industrial Communication Reliability Monitoring project.

Quick start (Python 3.8+):

1. Create a venv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the server:

```bash
python app.py
```

The simulator runs in a background thread and exposes these endpoints:

- `GET /network/status` - returns current nodes, links and metrics
- `POST /simulate/failure` - body: `{ "nodeId": "B" }` to fail a node
- `POST /simulate/restore` - body: `{ "nodeId": "B" }` to restore a node
- `POST /reset` - resets network and clears metrics
- `POST /simulate/random` - body: `{ "probability": 0.05 }` to set random fail probability
Additional endpoints and features:
- `GET /events` - Server-Sent Events stream of simulator state (JSON messages)
- `GET /metrics/history?limit=N` - returns recent persisted metric snapshots (N default 200)
- `POST /mqtt/publish` - body `{ "topic": "t", "message": {...} }` to publish a message to simulated MQTT broker
- `GET /mqtt/messages?topic=<topic>&limit=N` - retrieve recent messages for a topic
- `POST /mqtt/mode` - body `{ "enabled": true }` to enable/disable simulator MQTT publish mode (simulator will publish metrics to topic `sim/metrics` each tick when enabled)

Persistence:
- Metrics snapshots are stored in `metrics.db` (SQLite) under the backend directory. The simulator writes a snapshot each tick.

External MQTT broker (optional):
- To publish metrics to a real MQTT broker, set the environment variable `MQTT_BROKER` to the broker host (e.g. `localhost`) and optionally `MQTT_BROKER_PORT` (default 1883). The simulator will attempt to connect on startup and publish metric payloads to topic `sim/metrics` when MQTT mode is enabled (`POST /mqtt/mode`).


The frontend can poll `/network/status` or call endpoints to inject faults.

