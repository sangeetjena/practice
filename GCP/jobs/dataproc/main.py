import argparse
import json
import logging

from shared.runtime import dates, fetch_partner_day, validate_window


def aggregate_sales(frame):
    from pyspark.sql import functions as f

    required = ("order_id", "customer_id", "event_date", "amount_cents")
    invalid = frame.filter(
        f.col("order_id").isNull()
        | (f.length("order_id") == 0)
        | f.col("customer_id").isNull()
        | (f.length("customer_id") == 0)
        | f.col("event_date").isNull()
        | f.to_date("event_date", "yyyy-MM-dd").isNull()
        | f.col("amount_cents").isNull()
        | (f.col("amount_cents") < 0)
    )
    if invalid.limit(1).count():
        raise ValueError("Input violates the order contract")
    clean = frame.select(*required).dropDuplicates(list(required))
    return clean.groupBy("event_date").agg(
        f.count("order_id").alias("order_count"),
        f.sum("amount_cents").alias("revenue_cents"),
        f.countDistinct("customer_id").alias("customer_count"),
    )


def fetch_partition(day_iterator, api_url, secret_version):
    # Runs on executors, not the driver. Only a secret resource name is serialized.
    from shared.authentication.secrets import read_secret

    api_key = read_secret(secret_version)
    for day in day_iterator:
        for row in fetch_partner_day(api_url, api_key, day):
            if row["event_date"] != day:
                raise ValueError("Partner returned data outside the requested day")
            yield json.dumps(row)


def run(argv=None):
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as f
    from pyspark.sql.types import LongType, StringType, StructField, StructType

    parser = argparse.ArgumentParser()
    parser.add_argument("--use_case", choices=["daily_sales", "partner_extract"], required=True)
    for key in (
        "input_uri",
        "output_uri",
        "start_date",
        "end_date",
        "run_id",
        "target_project",
        "config_hash",
    ):
        parser.add_argument(f"--{key}", required=True)
    for key in ("api_url", "secret_version", "bt_instance", "bt_table", "bt_family", "bt_app_profile"):
        parser.add_argument(f"--{key}", default="")
    args = parser.parse_args(argv)
    validate_window(args.start_date, args.end_date)
    spark = SparkSession.builder.appName(f"{args.use_case}-{args.run_id}").getOrCreate()
    spark.conf.set("spark.sql.session.timeZone", "UTC")
    logging.info("Starting %s run=%s config=%s", args.use_case, args.run_id, args.config_hash)
    output = f"{args.output_uri.rstrip('/')}/start={args.start_date}/end={args.end_date}/run={args.run_id}"
    schema = StructType(
        [
            StructField("order_id", StringType()),
            StructField("customer_id", StringType()),
            StructField("event_date", StringType()),
            StructField("amount_cents", LongType()),
        ]
    )
    try:
        if args.use_case == "partner_extract":
            if not args.api_url or not args.secret_version:
                raise ValueError("API extraction needs api_url and secret_version")
            days = list(dates(args.start_date, args.end_date))
            # At most four API callers in this example; provider rate limits may need tighter control.
            records = spark.sparkContext.parallelize(days, min(len(days), 4)).mapPartitions(
                lambda partition: fetch_partition(partition, args.api_url, args.secret_version)
            )
            frame = spark.read.schema(schema).option("mode", "FAILFAST").json(records)
        else:
            paths = [
                f"{args.input_uri.rstrip('/')}/event_date={day}/*.jsonl"
                for day in dates(args.start_date, args.end_date)
            ]
            frame = spark.read.schema(schema).option("mode", "FAILFAST").json(paths)
            frame = frame.filter(
                (f.col("event_date") >= args.start_date) & (f.col("event_date") < args.end_date)
            )
            frame = aggregate_sales(frame)
        # A fresh run gets its own path. Never overwrite an earlier successful backfill.
        frame.write.mode("errorifexists").parquet(output)
    finally:
        spark.stop()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run()
