"""Train a daily next-close direction logistic model on historical database rows."""

from __future__ import annotations

import argparse
import asyncio
import os
from datetime import datetime, timezone, timedelta
from uuid import uuid4

import numpy as np
import torch

from ml_infra.artifact import save_artifact
from ml_infra.data import load_history, pe_as_of
from ml_infra.features import FEATURE_NAMES, FEATURE_VERSION, MIN_BARS, as_vector, make_features


def build_dataset(bars: list[dict], fundamentals: list[dict]) -> tuple[np.ndarray, np.ndarray, list[str]]:
    if len(bars) <= MIN_BARS:
        raise ValueError(
            f"TimescaleDB market_bars supplied {len(bars)} distinct daily bars; "
            f"at least {MIN_BARS + 1} are needed for one labeled example. "
            "Check symbol, interval='1d', adjusted=false, and Timescale ingestion. "
            "Postgres market_events rows are not used as training bars."
        )
    features: list[list[float]] = []
    labels: list[float] = []
    cutoffs: list[str] = []
    # Label is the next daily close; the feature row uses only observations available at cutoff.
    for i in range(MIN_BARS - 1, len(bars) - 1):
        # Daily bar_time is exchange-local midnight. Use next midnight as a
        # conservative point after the session; backfill observed_at is ingest time.
        cutoff = bars[i]["bar_time"] + timedelta(days=1)
        history = bars[: i + 1]
        if len(history) < MIN_BARS:
            continue
        row = make_features(history, pe_as_of(fundamentals, cutoff))
        features.append(as_vector(row))
        labels.append(float(bars[i + 1]["close"] > bars[i]["close"]))
        cutoffs.append(cutoff.isoformat())
    if len(features) < 30:
        raise ValueError(
            f"Need at least 30 labeled examples, but {len(bars)} distinct TimescaleDB daily bars "
            f"produced {len(features)}. At least {MIN_BARS + 30} bars are required."
        )
    return np.asarray(features, dtype=np.float32), np.asarray(labels, dtype=np.float32), cutoffs


def train_array(x: np.ndarray, y: np.ndarray, *, epochs: int, require_gpu: bool) -> dict:
    if require_gpu and not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable; install CUDA-enabled PyTorch or omit --require-gpu")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(42)
    split = int(len(x) * 0.8)
    if split < 20 or len(x) - split < 5:
        raise ValueError("insufficient chronological train/test rows")
    mean = x[:split].mean(axis=0)
    scale = x[:split].std(axis=0)
    scale[scale < 1e-8] = 1.0
    train_x = torch.tensor((x[:split] - mean) / scale, device=device)
    train_y = torch.tensor(y[:split].reshape(-1, 1), device=device)
    model = torch.nn.Linear(x.shape[1], 1).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.02, weight_decay=0.01)
    for _ in range(epochs):
        optimizer.zero_grad()
        loss = torch.nn.functional.binary_cross_entropy_with_logits(model(train_x), train_y)
        loss.backward()
        optimizer.step()
    weights = model.weight.detach().cpu().numpy().ravel().tolist()
    bias = float(model.bias.detach().cpu().item())
    test_scores = ((x[split:] - mean) / scale) @ np.asarray(weights) + bias
    test_prob = 1 / (1 + np.exp(-np.clip(test_scores, -50, 50)))
    accuracy = float(np.mean((test_prob >= 0.5) == y[split:]))
    base_rate = float(np.mean(y[split:]))
    return {
        "model_name": "daily-logistic-direction", "model_version": str(uuid4()),
        "feature_version": FEATURE_VERSION, "feature_names": list(FEATURE_NAMES),
        "target": "next_daily_close_up", "mean": mean.tolist(), "scale": scale.tolist(),
        "weights": weights, "bias": bias, "train_rows": split, "test_rows": len(x) - split,
        "test_accuracy": accuracy, "test_positive_rate": base_rate,
        "device": str(device), "trained_at": datetime.now(timezone.utc).isoformat(),
        "status": "candidate",
    }


async def run(args: argparse.Namespace) -> dict:
    timescale_url = os.environ.get("ML_TIMESCALE_URL")
    postgres_url = os.environ.get("ML_DATABASE_URL")
    if not timescale_url or not postgres_url:
        raise ValueError("ML_TIMESCALE_URL and ML_DATABASE_URL are required")
    bars, fundamentals = await load_history(timescale_url, postgres_url, args.symbol)
    x, y, cutoffs = build_dataset(bars, fundamentals)
    artifact = train_array(x, y, epochs=args.epochs, require_gpu=args.require_gpu)
    artifact["symbol"] = args.symbol.upper()
    artifact["training_cutoff"] = cutoffs[int(len(x) * 0.8) - 1]
    artifact["test_cutoff"] = cutoffs[-1]
    save_artifact(args.output, artifact)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--output", default="artifacts/candidate.json")
    parser.add_argument("--epochs", type=int, default=300)
    parser.add_argument("--require-gpu", action="store_true")
    args = parser.parse_args()
    result = asyncio.run(run(args))
    print({key: result[key] for key in ("model_version", "device", "train_rows", "test_rows", "test_accuracy", "status")})


if __name__ == "__main__":
    main()
