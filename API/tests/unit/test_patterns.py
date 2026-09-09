from typing import Any

import pytest
from pydantic import ValidationError

from api_interview_lab.patterns.dataclass_pattern import extract_with_dataclasses
from api_interview_lab.patterns.pandas_pattern import extract_with_pandas, revenue_by_product
from api_interview_lab.patterns.pydantic_pattern import OrderPayload, extract_with_pydantic


class StubOrderClient:
    def fetch_all_raw(self, page_size: int = 100) -> list[dict[str, Any]]:
        return [
            {
                "id": "1",
                "customer_id": "c1",
                "product": "Keyboard",
                "quantity": "2",
                "unit_price": "10.5",
                "status": "paid",
                "revenue": 21,
            },
            {
                "id": "2",
                "customer_id": "c2",
                "product": "Keyboard",
                "quantity": 3,
                "unit_price": 10,
                "status": "paid",
                "revenue": 30,
            },
        ]


def test_dataclass_conversion() -> None:
    record = extract_with_dataclasses(StubOrderClient())[0]
    assert record.quantity == 2


def test_pydantic_rejects_invalid_quantity() -> None:
    with pytest.raises(ValidationError):
        OrderPayload(
            id="1", customer_id="1", product="Keyboard",
            quantity=0, unit_price=10, status="created",
        )


def test_pydantic_extracts_api_response() -> None:
    result = extract_with_pydantic(StubOrderClient())
    assert result[0].revenue == 21


def test_pandas_aggregation() -> None:
    result = revenue_by_product(extract_with_pandas(StubOrderClient()))
    assert result.iloc[0].to_dict() == {
        "product": "Keyboard", "orders": 2, "units": 5, "revenue": 51.0
    }
