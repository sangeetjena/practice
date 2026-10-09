"""Typed local model client. HTTP prediction only; persistence is explicitly separate."""

import httpx
from pydantic import validate_call

from stock_research.models.local_model import (
    FeatureSnapshot,
    ModelPrediction,
    PredictInput,
    PredictOutput,
)


class LocalModelClient:
    def __init__(self, endpoint: str, token: str | None = None, client=None):
        self.endpoint, self.token, self.client = endpoint.rstrip("/"), token, client

    @validate_call
    async def predict(self, request: PredictInput) -> PredictOutput:
        """Invoke the deployed ML_INFRA model with validated versioned features.

        No DB connection or writes. A supplied snapshot directly calls POST /predict.
        Only when explicitly allowed may GET /features/{symbol} obtain server-side
        features. Credentials and endpoint are application-bound, never LLM inputs.
        """
        headers = {"X-Model-Token": self.token} if self.token else {}
        if not self.endpoint:
            raise ValueError("STOCK_MODEL_URL is required")
        client = self.client or httpx.AsyncClient(timeout=30)
        try:
            snapshot = request.snapshot
            if snapshot is None:
                if not request.allow_feature_fetch:
                    raise ValueError("DB-free prediction requires an explicit feature snapshot")
                response = await client.get(
                    f"{self.endpoint}/features/{request.symbol}", headers=headers
                )
                response.raise_for_status()
                snapshot = FeatureSnapshot.model_validate(response.json())
            if snapshot.symbol != request.symbol:
                raise ValueError("feature symbol does not match requested stock")
            if request.latest_cutoff and snapshot.cutoff_at > request.latest_cutoff:
                raise ValueError("model features follow the evidence cutoff")
            response = await client.post(
                f"{self.endpoint}/predict", json=snapshot.model_dump(mode="json"), headers=headers
            )
            response.raise_for_status()
            prediction = ModelPrediction.model_validate(response.json())
            if (
                prediction.feature_version
                and prediction.feature_version != snapshot.feature_version
            ):
                raise ValueError("returned feature version mismatch")
            return PredictOutput(snapshot=snapshot, prediction=prediction)
        finally:
            if self.client is None:
                await client.aclose()
