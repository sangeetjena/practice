"""Call deployed ML_INFRA model and persist its result in the stock database."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import datetime
from uuid import uuid4

import httpx

from stock_research.config import get_settings
from stock_research.storage.postgres import PostgresStore


async def run(symbol: str) -> dict:
    settings = get_settings()
    if not settings.database_url:
        raise ValueError("STOCK_DATABASE_URL is required")
    endpoint = os.environ.get("STOCK_MODEL_URL")
    if not endpoint:
        raise ValueError("STOCK_MODEL_URL is required")
    token = os.environ.get("STOCK_MODEL_TOKEN")
    headers = {"X-Model-Token": token} if token else {}
    async with httpx.AsyncClient(timeout=30) as client:
        feature_response = await client.get(f"{endpoint.rstrip('/')}/features/{symbol.upper()}", headers=headers)
        feature_response.raise_for_status()
        snapshot = feature_response.json()
        prediction_response = await client.post(f"{endpoint.rstrip('/')}/predict", json=snapshot, headers=headers)
        prediction_response.raise_for_status()
        prediction = prediction_response.json()
    store = await PostgresStore.connect(settings.database_url)
    try:
        await store.create_schema()
        async with store.pool.acquire() as connection:
            async with connection.transaction():
                await connection.fetchrow(
                    """INSERT INTO model_predictions
                       (prediction_id,symbol,cutoff_at,model_name,model_version,feature_version,
                        features,target,probability_up)
                       VALUES ($1,$2,$3,$4,$5,$6,$7::jsonb,$8,$9)
                       ON CONFLICT (symbol,cutoff_at,model_name,model_version)
                       DO UPDATE SET features=EXCLUDED.features, probability_up=EXCLUDED.probability_up
                       RETURNING prediction_id""",
                    uuid4(), snapshot["symbol"], datetime.fromisoformat(snapshot["cutoff_at"]), prediction["model_name"],
                    prediction["model_version"], snapshot["feature_version"],
                    json.dumps(snapshot["features"]), prediction["target"], prediction["probability_up"],
                )
                all_predictions = await connection.fetch(
                    """SELECT prediction_id, model_name, model_version, target, probability_up
                       FROM model_predictions WHERE symbol=$1 AND cutoff_at=$2
                       ORDER BY model_name, model_version""",
                    snapshot["symbol"], datetime.fromisoformat(snapshot["cutoff_at"]),
                )
                summary = {"symbol": snapshot["symbol"], "cutoff_at": snapshot["cutoff_at"],
                           "features": snapshot["features"], "predictions": [
                               {**dict(item), "prediction_id": str(item["prediction_id"])}
                               for item in all_predictions],
                           "final_assessment": None, "status": "model_only"}
                await connection.execute(
                    """INSERT INTO stock_summary_daily (symbol,cutoff_at,summary)
                       VALUES ($1,$2,$3::jsonb)
                       ON CONFLICT (symbol,cutoff_at) DO UPDATE SET summary=EXCLUDED.summary""",
                    snapshot["symbol"], datetime.fromisoformat(snapshot["cutoff_at"]), json.dumps(summary),
                )
        return summary
    finally:
        await store.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args.symbol)), indent=2))


if __name__ == "__main__":
    main()
