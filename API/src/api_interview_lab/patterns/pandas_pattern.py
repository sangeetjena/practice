from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {"id", "customer_id", "product", "quantity", "unit_price", "status"}


def load_orders_frame(csv_path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(csv_path)
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing CSV columns: {sorted(missing)}")
    frame = frame.assign(revenue=frame["quantity"] * frame["unit_price"])
    return frame


def revenue_by_product(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.groupby("product", as_index=False)
        .agg(orders=("id", "count"), units=("quantity", "sum"), revenue=("revenue", "sum"))
        .sort_values("revenue", ascending=False)
        .reset_index(drop=True)
    )

