"""Send a saved feature snapshot to the deployed prediction endpoint."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import httpx


def predict_file(path: str, endpoint: str, token: str) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("test file must contain a JSON object")
    required = {"symbol", "cutoff_at", "feature_version", "features"}
    if not required.issubset(payload):
        raise ValueError(f"test file is missing: {sorted(required - payload.keys())}")
    response = httpx.post(
        f"{endpoint.rstrip('/')}/predict",
        json=payload,
        headers={"X-Model-Token": token},
        timeout=30,
    )
    if response.status_code == 422:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise ValueError(f"Prediction request rejected (422): {detail}")
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict from a JSON feature test file")
    parser.add_argument("--file", default="tests/predict.json")
    parser.add_argument("--url", default=os.environ.get("ML_MODEL_URL", "http://127.0.0.1:8000"))
    args = parser.parse_args()
    token = os.environ.get("ML_MODEL_TOKEN")
    if not token:
        parser.error("ML_MODEL_TOKEN is required")
    print(json.dumps(predict_file(args.file, args.url, token), indent=2))


if __name__ == "__main__":
    main()
