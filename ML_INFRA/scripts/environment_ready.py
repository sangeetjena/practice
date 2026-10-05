"""Exit successfully when the ML_INFRA virtual environment needs no installation."""

from __future__ import annotations

import hashlib
import importlib.metadata
import importlib.util
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_FILE = ROOT / "pyproject.toml"
MARKER = ROOT / ".venv" / ".ml-infra-pyproject.sha256"
MODULES = (
    "ml_infra", "pydantic", "pydantic_settings", "asyncpg", "numpy", "torch",
    "fastapi", "uvicorn", "httpx", "pytest", "ruff", "mypy",
)


def ready() -> bool:
    project = tomllib.loads(PROJECT_FILE.read_text(encoding="utf-8"))
    fingerprint = hashlib.sha256(PROJECT_FILE.read_bytes()).hexdigest()
    if MARKER.exists() and MARKER.read_text(encoding="utf-8").strip() != fingerprint:
        return False
    try:
        distribution = importlib.metadata.distribution(project["project"]["name"])
    except importlib.metadata.PackageNotFoundError:
        return False
    if distribution.version != project["project"]["version"]:
        return False
    if any(importlib.util.find_spec(module) is None for module in MODULES):
        return False
    if subprocess.run(
        [sys.executable, "-m", "pip", "check"], capture_output=True, text=True, check=False
    ).returncode != 0:
        return False
    MARKER.write_text(fingerprint + "\n", encoding="utf-8")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if ready() else 1)
