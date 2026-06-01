# Smart Industrial Safety Monitoring Backend

Flask API and Python simulation engine for a SCADA-inspired industrial safety dashboard. The backend simulates hazardous plant sensors, detects abnormal conditions, calculates GREEN to BLACK risk levels, triggers emergency response actions, and keeps communication reliability as a supporting safety layer.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Server runs on `http://localhost:5000`.

## Main Endpoints

- `GET /network/status`
- `POST /api/simulate` with events such as `chemical_leak`, `radiation_spike`, `methane_explosion`, `communication_loss_shutdown`
- `POST /simulate/failure` body: `{ "nodeId": "B" }`
- `POST /simulate/restore` body: `{ "nodeId": "B" }`
- `POST /simulate/link-failure` body: `{ "source": "B", "target": "C" }`
- `POST /simulate/link-restore` body: `{ "source": "B", "target": "C" }`
- `POST /reset`
- `GET /metrics/history?limit=60`
- `GET /alerts?limit=40`
- `GET /logs?limit=100`

## Simulation Behavior

- Simulates temperature, pressure, toxic gas, radiation, methane, smoke, oxygen, and humidity sensors.
- Calculates GREEN, YELLOW, ORANGE, RED, and BLACK risk states.
- Converts communication packet loss into missed sensor readings and delayed alarm/shutdown delivery.
- Tracks plant safety score, alarm delivery rate, ESD success rate, MTBF, MTTR, and incident logs.
