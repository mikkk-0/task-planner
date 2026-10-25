#!/usr/bin/env bash
set -euo pipefail
SCRIPT_PATH="$(readlink -f "$0")"
PROJECT_DIR="$(dirname "$SCRIPT_PATH")"
cd "$PROJECT_DIR"
if [[ ! -x .venv/bin/python ]] || ! .venv/bin/python -c 'import pip' >/dev/null 2>&1; then
  python3 -m venv --clear .venv
fi
if ! .venv/bin/python -c 'import PySide6' >/dev/null 2>&1; then
  .venv/bin/python -m pip install -q -r requirements.txt
fi
nohup .venv/bin/python main.py >/dev/null 2>&1 </dev/null &
