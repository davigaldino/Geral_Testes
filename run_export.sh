#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Export variables from .env if present
if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

mkdir -p output

PYTHON_BIN="python3"
if [ -x "$SCRIPT_DIR/.venv/bin/python" ]; then
  PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
fi

exec "$PYTHON_BIN" "$SCRIPT_DIR/sharepoint_export.py"

