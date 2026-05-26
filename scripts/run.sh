#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${1:-8000}"
HOST="${HOST:-127.0.0.1}"
UVICORN="$ROOT/.venv/bin/uvicorn"

if [ ! -x "$UVICORN" ]; then
  echo "error: missing uvicorn at $UVICORN" >&2
  exit 1
fi

list_port_pids() {
  if command -v lsof >/dev/null 2>&1; then
    lsof -t -nP -iTCP:"$PORT" -sTCP:LISTEN || true
    return 0
  fi

  if command -v ss >/dev/null 2>&1; then
    ss -ltnp "( sport = :$PORT )" 2>/dev/null \
      | awk 'match($0, /pid=([0-9]+)/, m) { print m[1] }' \
      | sort -u
    return 0
  fi

  return 1
}

PIDS="$(list_port_pids | tr '\n' ' ' | sed 's/[[:space:]]\+$//')"
if [ -n "$PIDS" ]; then
  echo "port $PORT is already in use by: $PIDS"
  kill $PIDS
  sleep 1
fi

exec "$UVICORN" main:app --host "$HOST" --port "$PORT"
