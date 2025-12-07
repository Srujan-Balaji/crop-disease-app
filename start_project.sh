#!/bin/bash
# start_project.sh - start backend (uvicorn) using the venv python, then open frontend

set -euo pipefail
cd "$(dirname "$0")"

echo "🔎 Project folder: $(pwd)"

# --- activate venv (works if venv is at ./venv) ---
if [ -f "./venv/bin/activate" ]; then
  echo "🔁 Activating venv (./venv)..."
  # shellcheck disable=SC1091
  source ./venv/bin/activate
else
  echo "⚠️  No ./venv found. Create one with: python3 -m venv venv"
  exit 1
fi

# --- ensure uvicorn accessible via the venv python ---
if ! python -m uvicorn --help >/dev/null 2>&1; then
  echo "⚠️  uvicorn not installed in venv. Installing minimal requirements..."
  python -m pip install --upgrade pip
  python -m pip install uvicorn fastapi
fi

# --- start backend using venv's python to guarantee correct environment ---
echo "🚀 Starting backend (uvicorn) on http://127.0.0.1:8000 ..."
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000 &
SERVER_PID=$!

# short wait so server logs appear before opening browser
sleep 1

# --- open the frontend in the default browser ---
FRONTEND_PATH="frontend/index.html"
if [ -f "$FRONTEND_PATH" ]; then
  echo "🌐 Opening frontend: $FRONTEND_PATH"
  # macOS
  if command -v open >/dev/null 2>&1; then
    open "$FRONTEND_PATH"
  # linux (xdg-open)
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$FRONTEND_PATH"
  else
    echo "⚠️  Can't auto-open browser. Open manually: http://127.0.0.1:5500/frontend/index.html (or open the file)"
  fi
else
  echo "⚠️  Frontend file not found at $FRONTEND_PATH"
fi

echo "ℹ️  Backend PID: $SERVER_PID"
echo "✅ Project started. To stop the server press CTRL+C in this terminal or run: kill $SERVER_PID"

# wait for server to exit (so terminal stays attached)
wait $SERVER_PID