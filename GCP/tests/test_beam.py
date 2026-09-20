import json

import pytest

beam = pytest.importorskip("apache_beam")
from apache_beam.testing.test_pipeline import TestPipeline as BeamPipeline  # noqa: E402
from apache_beam.testing.util import assert_that, equal_to  # noqa: E402

from jobs.dataflow.transforms import ParseOrders, bigtable_row, metric_pair  # noqa: E402


def test_clean_orders_deduplicates_and_filters_dates():
    row = {"order_id": "o1", "customer_id": "c1", "event_date": "2026-09-18", "amount_cents": 100}
    outside = {**row, "order_id": "o2", "event_date": "2026-09-20"}
    with BeamPipeline() as pipeline:
        result = (
            pipeline
            | beam.Create([json.dumps(row), json.dumps(row), json.dumps(outside)])
            | ParseOrders("2026-09-18", "2026-09-20")
        )
        assert_that(result, equal_to([row]))


def test_bigtable_metrics_use_stable_customer_day_keys():
    pair = metric_pair({"customer_id": "c1", "event_date": "2026-09-18", "amount_cents": 100})
    first = bigtable_row(pair, "metrics")
    second = bigtable_row(pair, "metrics")
    assert first.row_key == second.row_key
    assert first.row_key.endswith(b"#c1#2026-09-18")
    assert [vars(mutation) for mutation in first._get_mutations()] == [
        vars(mutation) for mutation in second._get_mutations()
    ]
