# Working workload examples

All examples share an inclusive `start_date`, exclusive `end_date`, and `run_id`. The raw order contract is:

```json
{"order_id":"o-001","customer_id":"c-001","event_date":"2026-09-18","amount_cents":1200}
```

Input partitions use `orders/event_date=YYYY-MM-DD/*.jsonl`. The fixture includes an exact duplicate to exercise deduplication.

## Beam: order cleansing

`dataflow/main.py` with `use_case=clean_orders` reads each day's JSONL files, validates rows, filters the requested window, removes exact duplicates, and writes normalized JSONL. Amounts remain integer cents.

Run locally after installing `requirements/beam.lock`:

```powershell
python -m jobs.dataflow.main --use_case clean_orders --input_uri jobs/fixtures/orders/ --output_uri build/local-clean/ --start_date 2026-09-18 --end_date 2026-09-20 --run_id local-001 --target_project local-test --config_hash local --runner DirectRunner
```

Expected output: three distinct orders totaling 2,500 cents, split over two dates.

## PySpark: daily sales

`dataproc/main.py` with `use_case=daily_sales` validates the explicit input schema, removes exact duplicates, groups by day, and writes order count, revenue cents, and distinct customer count as Parquet.

With PySpark 3.5.3 and Java 17 installed:

```powershell
spark-submit --master 'local[2]' jobs/dataproc/main.py --use_case daily_sales --input_uri jobs/fixtures/orders/ --output_uri build/local-sales/ --start_date 2026-09-18 --end_date 2026-09-20 --run_id local-001 --target_project local-test --config_hash local
```

Run from `GCP` with the package installed in your active Python environment; the cloud image supplies shared modules on both driver and executors. Expected daily revenues are 2,000 and 500 cents. Linux is the supported Spark CI environment; native Windows may require additional Hadoop/Java setup.

## Beam: authenticated API extraction

Copy the `beam-partner` and `secrets.partner` settings from the optional configuration example into an environment file, enable NAT, and replace `api.example.com` with a controlled test endpoint.

`FetchPartner` receives only a Secret Manager version name in its constructor. Its worker-side `setup()` fetches the token once per DoFn instance. Each element is a date; the example calls an HTTPS endpoint using the `X-API-Key` header and a `date` query parameter, validates returned orders, and writes JSONL.

This is a bounded integration example, not a universal vendor API client. It intentionally does not guess pagination, rate-limiting or provider-specific retry contracts. Per-day responses are limited to 10 MB and redirects are rejected.

## PySpark: executor-side API extraction

The `spark-api` configuration runs `use_case=partner_extract`. Each executor partition resolves the same numeric secret version through its runtime identity, fetches the assigned dates, and returns JSON records. Spark writes Parquet. The token is not fetched on the driver or captured in the serialized task closure.

The example limits the API-fetching RDD to at most four partitions. Spark may retry a task, so use read-only or otherwise idempotent API calls. A provider-wide rate limiter requires additional design.

## Beam: Bigtable customer/day metrics

Enable Bigtable and the `bt-metrics` job using the optional configuration fragment. The pipeline sums integer cents by customer/day, then writes through the Terraform-created batch app profile. The sink batches up to 100 rows per request and checks per-row status.

Keys are `SALT#CUSTOMER_ID#YYYY-MM-DD`, where the salt is a short customer hash. The family is configured in YAML, the column is `amount_cents`, and the timestamp is the day's UTC midnight. Replays replace the same cell version. Audit JSONL is emitted only after the corresponding mutation batch succeeds.

This is an example key design: choose keys and GC/retention policies based on actual query patterns and load. Multi-row updates are not transactional and overlapping runs can overwrite the same aggregate.

## Upload fixture data for a GCP smoke test

Use an authorized data-owner account, since the runtime identities intentionally cannot write raw input:

```powershell
gcloud storage cp --recursive jobs/fixtures/orders gs://YOUR_RAW_BUCKET/
gcp-platform run clean-orders --env dev --outputs build/dev/outputs.json --start-date 2026-09-18 --end-date 2026-09-20 --run-id smoke-clean-01 --execute
gcp-platform run daily-sales --env dev --outputs build/dev/outputs.json --start-date 2026-09-18 --end-date 2026-09-20 --run-id smoke-sales-01 --execute
```

The fixture dates are fixed, so invoke them manually. A production schedule selects yesterday's date and expects your real ingestion process to have created that partition.
