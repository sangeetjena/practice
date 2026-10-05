"""Shared, versioned train/serve feature contract using completed daily bars."""

from __future__ import annotations

from datetime import datetime
from math import log

FEATURE_VERSION = "daily-v1"
FEATURE_NAMES = ("return_1", "return_5", "sma_5_gap", "sma_20_gap", "volume_ratio_5", "volatility_5", "pe_ratio")
MIN_BARS = 21


def make_features(bars: list[dict], pe_ratio: float | None = None) -> dict[str, float]:
    """Bars must be ascending and observed no later than the requested cutoff."""
    if len(bars) < MIN_BARS:
        raise ValueError(f"at least {MIN_BARS} completed bars are required")
    closes = [float(b["close"]) for b in bars]
    volumes = [float(b["volume"]) for b in bars]
    if min(closes) <= 0 or min(volumes[-5:]) < 0:
        raise ValueError("invalid close or volume")
    returns = [log(closes[i] / closes[i - 1]) for i in range(-5, 0)]
    current = closes[-1]
    average_volume = sum(volumes[-6:-1]) / 5
    return {
        "return_1": returns[-1],
        "return_5": log(current / closes[-6]),
        "sma_5_gap": current / (sum(closes[-5:]) / 5) - 1,
        "sma_20_gap": current / (sum(closes[-20:]) / 20) - 1,
        "volume_ratio_5": volumes[-1] / average_volume if average_volume > 0 else 0.0,
        "volatility_5": (sum((r - sum(returns) / 5) ** 2 for r in returns) / 5) ** 0.5,
        "pe_ratio": float(pe_ratio) if pe_ratio is not None else 0.0,
    }


def as_vector(features: dict[str, float]) -> list[float]:
    if set(features) != set(FEATURE_NAMES):
        raise ValueError("feature schema mismatch")
    return [features[name] for name in FEATURE_NAMES]
