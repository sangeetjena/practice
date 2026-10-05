"""Private read-only prediction endpoint deployed by ML_INFRA."""

from __future__ import annotations

import os
from functools import lru_cache

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from ml_infra.artifact import load_artifact, predict
from ml_infra.data import load_history, pe_as_of
from ml_infra.features import MIN_BARS, make_features
from ml_infra.features import FEATURE_VERSION


class PredictRequest(BaseModel):
    symbol: str
    cutoff_at: str
    feature_version: str
    features: dict[str, float]


app = FastAPI(title="Stock logistic model serving")


def authorize(token: str | None) -> None:
    expected = os.environ.get("ML_MODEL_TOKEN")
    if not expected:
        raise HTTPException(status_code=503, detail="model token is not configured")
    if token != expected:
        raise HTTPException(status_code=401, detail="unauthorized")


@lru_cache(maxsize=1)
def model() -> dict:
    return load_artifact(os.environ.get("ML_ARTIFACT_PATH", "/models/model.json"))


@app.get("/health")
def health() -> dict[str, str]:
    artifact = model()
    return {"status": "ok", "model_version": artifact["model_version"]}


@app.post("/predict")
def prediction(request: PredictRequest, x_model_token: str | None = Header(default=None)) -> dict:
    authorize(x_model_token)
    artifact = model()
    if request.feature_version != FEATURE_VERSION or request.symbol.upper() != artifact["symbol"]:
        raise HTTPException(status_code=422, detail="feature version or symbol mismatch")
    try:
        probability = predict(artifact, request.features)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "model_name": artifact["model_name"], "model_version": artifact["model_version"],
        "target": artifact["target"], "probability_up": probability,
        "feature_version": FEATURE_VERSION,
    }


@app.get("/features/{symbol}")
async def features(symbol: str, x_model_token: str | None = Header(default=None)) -> dict:
    authorize(x_model_token)
    timescale_url = os.environ.get("ML_TIMESCALE_URL")
    postgres_url = os.environ.get("ML_DATABASE_URL")
    if not timescale_url or not postgres_url:
        raise HTTPException(status_code=503, detail="database URLs are not configured")
    bars, fundamentals = await load_history(timescale_url, postgres_url, symbol)
    if len(bars) < MIN_BARS:
        raise HTTPException(status_code=422, detail="insufficient daily bars")
    cutoff = bars[-1]["observed_at"]
    history = [bar for bar in bars if bar["observed_at"] <= cutoff]
    return {"symbol": symbol.upper(), "cutoff_at": cutoff.isoformat(),
            "feature_version": FEATURE_VERSION,
            "features": make_features(history, pe_as_of(fundamentals, cutoff))}
