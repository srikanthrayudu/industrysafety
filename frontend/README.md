# Industrial Communication Reliability Monitoring System (Frontend)

React + TypeScript dashboard for simulated industrial communication reliability.

## Run

```bash
npm install
npm run dev -- --host
```

Frontend runs on `http://localhost:5173` and calls backend via:

- `VITE_API_BASE` (default: `http://localhost:5000`)

## Views

- Home page
- Real-time Dashboard
- Logs page

## Dashboard Features

- Industrial node topology map
- Node fault injection and restore controls
- Reliability / packet loss / delay metrics
- Backup route activation status
- Alerts panel
- Charts (line, bar, pie)
