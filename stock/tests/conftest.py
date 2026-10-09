"""Keep framework runtime files inside the project while testing."""

import os
from pathlib import Path
from uuid import uuid4

import pytest

root = Path(__file__).resolve().parents[1] / ".state"
root.mkdir(exist_ok=True)
os.environ["CREWAI_STORAGE_DIR"] = str(root / "test-runtime")
os.environ["LOCALAPPDATA"] = str(root)
os.environ["OTEL_SDK_DISABLED"] = "true"


# Project-local temporary directories avoid restrictive OS temp permissions.


@pytest.fixture
def tmp_path():
    path = root / "tests" / str(uuid4())
    path.mkdir(parents=True)
    return path
