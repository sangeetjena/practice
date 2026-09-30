#!/usr/bin/env bash
set -euo pipefail

INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required to create INFRA/.venv. Install Python 3.11 or newer and retry." >&2
  exit 1
fi

if ! python3 -m ensurepip --version >/dev/null 2>&1; then
  python_version="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  echo "The system Python is missing ensurepip, so INFRA/.venv cannot be created yet." >&2
  echo "On Debian/Ubuntu, install the matching venv package, then rerun 'make setup':" >&2
  echo "  sudo apt update && sudo apt install python${python_version}-venv" >&2
  exit 1
fi

VENV_PYTHON="$INFRA_DIR/.venv/bin/python"
if [[ ! -x "$VENV_PYTHON" ]] || ! "$VENV_PYTHON" -m pip --version >/dev/null 2>&1; then
  if [[ -e "$INFRA_DIR/.venv" ]]; then
    echo "Removing incomplete INFRA/.venv before recreating it."
    rm -rf -- "$INFRA_DIR/.venv"
  fi
  echo "Creating isolated Python environment at $INFRA_DIR/.venv"
  python3 -m venv "$INFRA_DIR/.venv"
fi

"$VENV_PYTHON" -m pip install --disable-pip-version-check \
  --requirement "$INFRA_DIR/requirements-dev.txt"
"$VENV_PYTHON" -c 'import yaml; print("INFRA Python environment is ready (PyYAML " + yaml.__version__ + ")")'