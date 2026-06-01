# Industrial Communication Reliability Monitoring System (Backend)

Flask API + Python simulation engine for an Industry 4.0 communication reliability demo.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Server runs on `http://localhost:5000`.

## Endpoints

- `GET /network/status`
- `POST /simulate/failure` body: `{ "nodeId": "B" }`
- `POST /simulate/restore` body: `{ "nodeId": "B" }`
- `POST /simulate/random` body: `{ "probability": 0.08 }`
- `POST /reset`
- `GET /metrics/history?limit=60`
- `GET /alerts?limit=40`
- `GET /logs?limit=100`

## Simulation Behavior

- Simulates packet transfer each second.
- Injects random failures based on configured probability.
- Detects route switch from primary to backup path.
- Updates reliability, delay, packet loss, active/failed node counters.
- Produces alerts and event logs in memory.
