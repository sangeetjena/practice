#!/usr/bin/env bash
set -euo pipefail
required=(docker kind kubectl helm terraform make bash python3)
missing=()
for command_name in "${required[@]}"; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    missing+=("$command_name")
  fi
done

if ((${#missing[@]})); then
  printf 'Missing required tools: %s\n' "${missing[*]}" >&2
  echo "Install Docker Desktop (Windows/macOS) or Docker Engine (Linux), kind, kubectl, Helm, Terraform, Make, Bash, and Python 3 (python3 command)." >&2
  echo "On Windows, run the Bash scripts from WSL2 or Git Bash and enable Docker Desktop file sharing for the data directory." >&2
  exit 1
fi

INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INFRA_PYTHON="$INFRA_DIR/.venv/bin/python"
if [[ ! -x "$INFRA_PYTHON" ]] || ! "$INFRA_PYTHON" -c 'import yaml' >/dev/null 2>&1; then
  echo "INFRA/.venv is missing or incomplete. Run 'make setup' from INFRA/." >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker is installed but the Docker daemon is not available. Start Docker Desktop or Docker Engine." >&2
  exit 1
fi

echo "Prerequisites are installed and Docker is running."