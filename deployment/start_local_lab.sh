#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_STREAMLIT="$PROJECT_ROOT/.venv/bin/streamlit"
SYSTEM_PYTHON="$(command -v python3)"

if [[ ! -x "$VENV_STREAMLIT" ]]; then
  echo "Streamlit is not installed in $PROJECT_ROOT/.venv. Install the project requirements first." >&2
  exit 1
fi

# This Mac already has OpenCV, PyTorch, and Ultralytics in Python's user site;
# make them visible to the existing Streamlit virtual environment without copying or reinstalling them.
USER_SITE="$($SYSTEM_PYTHON -c 'import site; print(site.getusersitepackages())')"
cd "$PROJECT_ROOT"
export PYTHONPATH="$USER_SITE${PYTHONPATH:+:$PYTHONPATH}"
exec "$VENV_STREAMLIT" run app/main.py --server.address 127.0.0.1 --server.port "${PORT:-8501}"
