# Smart Industrial Safety Monitoring Frontend

React + TypeScript dashboard for a web-based SCADA-style industrial safety and emergency response simulator.

## Run

```bash
npm install
npm run dev -- --host
```

Frontend runs on `http://localhost:5173` and calls the backend through:

- `VITE_API_BASE` (default: `http://localhost:5000`)

## Views

- Dashboard
- Home
- Safety Analytics
- Incident Logs

## Dashboard Features

- Plant overview
- Safety sensor panel
- Hazard detection panel
- GREEN to BLACK risk meter
- Emergency alerts and response actions
- Safety communication health
- Industrial control network map
- Reliability and risk charts
- Incident timeline and JSON report export
