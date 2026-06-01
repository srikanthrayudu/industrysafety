#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-local}"

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
  if [[ -n "${FRONTEND_PID:-}" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi
}

if [[ "$MODE" == "--docker" || "$MODE" == "docker" ]]; then
  cd "$ROOT_DIR"
  exec docker compose up --build
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "Error: npm is not installed."
  exit 1
fi

if [[ -x "$ROOT_DIR/backend/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT_DIR/backend/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  echo "Error: Python is not installed."
  exit 1
fi

if [[ ! -d "$ROOT_DIR/frontend/node_modules" ]]; then
  (cd "$ROOT_DIR/frontend" && npm install)
fi

trap cleanup EXIT INT TERM

(
  cd "$ROOT_DIR/backend"
  "$PYTHON_BIN" app.py
) &
BACKEND_PID=$!

(
  cd "$ROOT_DIR/frontend"
  VITE_API_BASE="${VITE_API_BASE:-http://localhost:5000}" npm run dev -- --host 0.0.0.0
) &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Frontend URL: http://localhost:5173 (Vite may auto-select another port if busy)"
echo "Press Ctrl+C to stop both services."

wait -n "$BACKEND_PID" "$FRONTEND_PID"
