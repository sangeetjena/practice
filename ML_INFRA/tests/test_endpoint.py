import json

from fastapi.testclient import TestClient

from ml_infra.features import FEATURE_NAMES, FEATURE_VERSION
from ml_infra.serve import app, model


def test_predict_contract_and_auth(tmp_path, monkeypatch) -> None:
    artifact = {
        "symbol": "IBM", "model_name": "daily-logistic-direction", "model_version": "test-v1",
        "target": "next_daily_close_up", "feature_version": FEATURE_VERSION,
        "feature_names": list(FEATURE_NAMES), "mean": [0.0] * len(FEATURE_NAMES),
        "scale": [1.0] * len(FEATURE_NAMES), "weights": [0.0] * len(FEATURE_NAMES),
        "bias": 0.0,
    }
    path = tmp_path / "model.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    monkeypatch.setenv("ML_ARTIFACT_PATH", str(path))
    monkeypatch.setenv("ML_MODEL_TOKEN", "test-token")
    model.cache_clear()
    request = {"symbol": "IBM", "cutoff_at": "2026-09-30T20:00:00+00:00",
               "feature_version": FEATURE_VERSION,
               "features": {name: 0.0 for name in FEATURE_NAMES}}
    with TestClient(app) as client:
        assert client.post("/predict", json=request).status_code == 401
        response = client.post("/predict", json=request, headers={"X-Model-Token": "test-token"})
        assert response.status_code == 200
        assert response.json()["probability_up"] == 0.5
        assert response.json()["model_version"] == "test-v1"
    model.cache_clear()
