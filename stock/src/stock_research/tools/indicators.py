"""Versioned deterministic daily indicators, calculated on completed bars only."""

import math
from statistics import mean

VERSION = "daily-indicators-v1"


def indicators(bars: list[dict]) -> dict:
    if len(bars) < 35:
        return {"version": VERSION, "ready": False, "bar_count": len(bars)}
    closes = [float(b["close"]) for b in bars]
    if any(not math.isfinite(x) or x <= 0 for x in closes):
        raise ValueError("invalid closing prices")

    def ema(values, period):
        result = [values[0]]
        for value in values[1:]:
            result.append(value * (2 / (period + 1)) + result[-1] * (1 - 2 / (period + 1)))
        return result

    gains = [max(b - a, 0) for a, b in zip(closes, closes[1:])]
    losses = [max(a - b, 0) for a, b in zip(closes, closes[1:])]
    avg_gain, avg_loss = mean(gains[:14]), mean(losses[:14])
    for gain, loss in zip(gains[14:], losses[14:]):
        avg_gain = (avg_gain * 13 + gain) / 14
        avg_loss = (avg_loss * 13 + loss) / 14
    rsi = (
        50
        if avg_gain == avg_loss == 0
        else (100 if avg_loss == 0 else 100 - 100 / (1 + avg_gain / avg_loss))
    )
    macd = [a - b for a, b in zip(ema(closes, 12), ema(closes, 26))]
    ranges = [
        max(
            float(b["high"]) - float(b["low"]),
            abs(float(b["high"]) - prev),
            abs(float(b["low"]) - prev),
        )
        for b, prev in zip(bars[1:], closes)
    ]
    atr = mean(ranges[:14])
    for value in ranges[14:]:
        atr = (atr * 13 + value) / 14
    volume_mean = mean(float(b["volume"]) for b in bars[-21:-1])
    return {
        "version": VERSION,
        "ready": True,
        "bar_count": len(bars),
        "last_close": closes[-1],
        "last_bar_time": str(bars[-1]["bar_time"]),
        "sma20": mean(closes[-20:]),
        "sma50": mean(closes[-50:]) if len(closes) >= 50 else None,
        "ema20": ema(closes, 20)[-1],
        "rsi14": rsi,
        "atr14": atr,
        "macd": macd[-1],
        "macd_signal": ema(macd, 9)[-1],
        "support20": min(float(b["low"]) for b in bars[-21:-1]),
        "resistance20": max(float(b["high"]) for b in bars[-21:-1]),
        "volume": bars[-1]["volume"],
        "volume_ratio20": float(bars[-1]["volume"]) / volume_mean if volume_mean else None,
        "return20": closes[-1] / closes[-21] - 1,
    }
