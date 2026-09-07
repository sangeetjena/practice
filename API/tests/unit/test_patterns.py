from pathlib import Path

import pytest
from pydantic import ValidationError

from api_interview_lab.patterns.dataclass_pattern import OrderRecord
from api_interview_lab.patterns.pandas_pattern import load_orders_frame, revenue_by_product
from api_interview_lab.patterns.pydantic_pattern import OrderPayload


def test_dataclass_conversion() -> None:
    record = OrderRecord.from_dict(
        {"id": "1", "product": "Keyboard", "quantity": "2", "unit_price": "10.5"}
    )
    assert record.quantity == 2


def test_pydantic_rejects_invalid_quantity() -> None:
    with pytest.raises(ValidationError):
        OrderPayload(
            id="1", customer_id="1", product="Keyboard",
            quantity=0, unit_price=10, status="created",
        )


def test_pandas_aggregation(tmp_path: Path) -> None:
    path = tmp_path / "orders.csv"
    path.write_text(
        "id,customer_id,product,quantity,unit_price,status\n"
        "1,c1,Keyboard,2,10,paid\n2,c2,Keyboard,3,10,paid\n",
        encoding="utf-8",
    )
    result = revenue_by_product(load_orders_frame(path))
    assert result.iloc[0].to_dict() == {
        "product": "Keyboard", "orders": 2, "units": 5, "revenue": 50
    }

