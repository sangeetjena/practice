from __future__ import annotations

import pandas as pd

from api_interview_lab.patterns.source import OrderSource

REQUIRED_COLUMNS = {"id", "customer_id", "product", "quantity", "unit_price", "status"}


def extract_with_pandas(client: OrderSource) -> pd.DataFrame:
    """Fetch paginated JSON through the client, then normalize it into a DataFrame."""
    frame = pd.json_normalize(client.fetch_all_raw())
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing API fields: {sorted(missing)}")
    frame[["quantity", "unit_price"]] = frame[["quantity", "unit_price"]].apply(
        pd.to_numeric, errors="raise"
    )
    frame = frame.assign(revenue=frame["quantity"] * frame["unit_price"])
    return frame


def revenue_by_product(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.groupby("product", as_index=False)
        .agg(orders=("id", "count"), units=("quantity", "sum"), revenue=("revenue", "sum"))
        .sort_values("revenue", ascending=False)
        .reset_index(drop=True)
    )
