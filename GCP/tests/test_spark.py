import pytest

pytest.importorskip("pyspark")

from jobs.dataproc.main import aggregate_sales  # noqa: E402


@pytest.fixture(scope="module")
def spark():
    from pyspark.sql import SparkSession

    session = SparkSession.builder.master("local[2]").appName("gcp-template-tests").getOrCreate()
    yield session
    session.stop()


def test_daily_sales_aggregates_without_counting_exact_duplicates(spark):
    frame = spark.createDataFrame(
        [
            ("o1", "c1", "2026-09-18", 1200),
            ("o1", "c1", "2026-09-18", 1200),
            ("o2", "c2", "2026-09-18", 800),
        ],
        "order_id string, customer_id string, event_date string, amount_cents long",
    )
    row = aggregate_sales(frame).first()
    assert (row.order_count, row.revenue_cents, row.customer_count) == (2, 2000, 2)


def test_daily_sales_rejects_negative_amount(spark):
    frame = spark.createDataFrame(
        [("o1", "c1", "2026-09-18", -10)],
        "order_id string, customer_id string, event_date string, amount_cents long",
    )
    with pytest.raises(ValueError, match="contract"):
        aggregate_sales(frame)
