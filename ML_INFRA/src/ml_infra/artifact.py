"""Portable JSON artifact; no pickle loading in the serving process."""

from __future__ import annotations

import json
from pathlib import Path
from math import exp

from ml_infra.features import FEATURE_NAMES, FEATURE_VERSION, as_vector


def save_artifact(path: str, artifact: dict) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")


def load_artifact(path: str) -> dict:
    artifact = json.loads(Path(path).read_text(encoding="utf-8"))
    if artifact["feature_version"] != FEATURE_VERSION or artifact["feature_names"] != list(FEATURE_NAMES):
        raise ValueError("artifact feature contract mismatch")
    return artifact


def predict(artifact: dict, features: dict[str, float]) -> float:
    vector = as_vector(features)
    standardized = [(x - m) / s for x, m, s in zip(vector, artifact["mean"], artifact["scale"])]
    score = sum(x * w for x, w in zip(standardized, artifact["weights"])) + artifact["bias"]
    return 1 / (1 + exp(-max(-50, min(50, score))))
