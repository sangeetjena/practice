# Scheduling, backfills, ad hoc execution, and recovery

## Why Scheduler and Workflows?

Cloud Scheduler supplies cron triggers. Workflows validates inputs, claims the run, launches Dataflow or Dataproc, polls until terminal status, requests cancellation on a configured timeout, and surfaces failures. Scheduler's successful HTTP request means only that an execution was accepted; it does not mean the data job succeeded.

Terraform deploys one workflow per job and a Scheduler resource only for jobs with `schedule.enabled: true`. Prod enables the two core daily jobs by default; dev/preprod are manual. Every schedule stays paused until a release is deployed. Set `enabled: false` and apply to remove a trigger; it does not cancel a running execution.

Both scheduled examples read raw orders independently. The 02:00/03:00 cron times do not establish a dependency. If Spark must consume a Beam result, create a parent workflow with explicit wait-for-success and artifact handoff, or move that DAG to Composer. Never use "an hour later" as a substitute for a dependency check.

## Scheduled windows

A scheduled execution receives `{"scheduled": true}`. The workflow computes yesterday/today from its actual start time in **UTC**, then runs `[yesterday, today)`. Its run ID is `d-YYYY-MM-DD` for yesterday. The Scheduler timezone affects the clock time of the trigger only.

This policy is for one daily run. It is not a general calendar engine: it does not implement local business-day partitions, DST-specific windows, automatic catch-up, or one partition per missed trigger. A trigger delayed across a UTC date boundary uses its actual execution day's window. Monitor missed runs and use explicit backfills for gaps. Extend the window policy before using hourly schedules or local-time partitioning.

## Manual and backfill arguments

Use the same workflow for scheduled, ad hoc, and backfill jobs. Supported external arguments are `start_date`, `end_date`, and `run_id`. Dates must be valid ISO calendar dates, the end must be later than the start, and a window cannot exceed 366 days. The CLI requires a run ID; direct workflow calls can omit it to obtain an execution-derived ID.

One-day ad hoc run:

```powershell
gcp-platform run clean-orders --env dev --outputs build/dev/outputs.json --start-date 2026-09-18 --end-date 2026-09-19 --run-id adhoc-check-01 --execute
```

Month backfill:

```powershell
gcp-platform run daily-sales --env prod --outputs build/prod/outputs.json --start-date 2026-08-01 --end-date 2026-09-01 --run-id bf-aug-2026-v1 --execute
```

Leave off `--execute` to preview the request. Workflows receives:

```json
{"start_date":"2026-08-01","end_date":"2026-09-01","run_id":"bf-aug-2026-v1"}
```

It adds these fields to Flex Template parameters or PySpark `--start_date`, `--end_date`, and `--run_id` arguments. Project, service account, image digest, machine sizing, endpoint, and secret references come from the deployed specification. An operator cannot override them through an arbitrary extra JSON key; the workflow checks its allowlist independently of the CLI.

To add a new supported runtime argument, update workflow validation, CLI request validation, and the job parser together. Validate semantics before making a cloud API call. Keep privileged resource choices as reviewed deployment configuration.

## Run identity and duplicate prevention

Before submitting a job, Workflows creates a small JSON object in the control bucket at `runs/JOB/RUN_ID.json`, using the atomic GCS `ifGenerationMatch=0` precondition. It records the original execution ID, date window, and release. A second claim for the same job/run ID fails; an ambiguous launch response is not blindly retried.

This is **at-most-once submission per retained claim**, not exactly-once business processing. A failure after claiming but before launching leaves the claim in place. Inspect the recorded execution and service-side job before retrying with a new run ID. Claims are deliberately not auto-deleted, even after success or failure.

Different run IDs may run concurrently, even for overlapping date windows. There is no global concurrency semaphore or partition lock. Set appropriate quotas, worker limits, and operator procedures. Do not run overlapping Bigtable recomputations concurrently. Spark's API example allows up to four fetching partitions per job, which is not a provider-wide rate limit.

## Output and data quality

Outputs use `PREFIX/start=YYYY-MM-DD/end=YYYY-MM-DD/run=RUN_ID/`. Beam writes JSONL shards and Spark writes Parquet. Spark refuses an already-existing output path. Downstream consumers should read only a selected successful execution's output; partial output may remain after failure.

The order contract has string order/customer IDs, an ISO date, and nonnegative integer `amount_cents`. Exact duplicates are removed. Conflicting versions of the same order ID are **not** arbitrarily reconciled: both distinct records remain, so adapt the sample with a business-defined latest-event/version policy when needed. Missing input partitions and malformed input fail the batch. The example does not silently skip missing days or publish partial aggregates as successful results.

Bigtable uses salted customer/day keys and deterministic cell timestamps. Repeating a completed input window replaces the same aggregate cell rather than incrementing it. This does not make a multi-row job transactional. Failed runs may have updated some rows; rerun the complete affected window after investigating.

## Failures, timeouts, and cancellation

Workflow polling retries transient GET failures. Job creation calls are not automatically retried. A failed/cancelled Dataflow job or Dataproc batch fails the workflow. On `timeout_seconds`, Workflows requests Dataflow job cancellation or Dataproc **operation** cancellation. Cancellation is asynchronous; inspect the service until it actually stops. Dataproc also has a service-side TTL.

Cancelling a Workflows execution manually can leave its underlying job running. Cancel the Dataflow job or Dataproc batch separately and verify final status. A polling permission error or prolonged service outage can also leave a job running; the error alert is a prompt to inspect both layers.

Terraform creates a Monitoring alert policy for failed workflow executions. Initially it has no notification channels; configure your team's channels before relying on paging. Also monitor data arrival and missing successful daily runs, as a failure alert cannot detect a trigger that never ran. Platform logs include run IDs and configuration hashes, not secret values.

## First cloud smoke test

1. Deploy dev infrastructure and a release.
2. Upload the two fixture input partitions with an authorized data-owner identity.
3. Run `clean-orders` and `daily-sales` for `[2026-09-18, 2026-09-20)` using different job/run names as needed.
4. Wait for workflow success. Expect three cleaned order rows; sales totals of 2,000 cents on September 18 and 500 cents on September 19.
5. Verify the jobs used the intended private subnet and runtime service accounts.
6. Test an API example against a controlled endpoint and secret version; verify a runtime account without Secret Accessor cannot fetch it.
7. Enable Bigtable only when testing that sink, and verify one cell per customer/day plus audit JSONL.

Only then promote artifacts and enable the real production data feed. Mock Terraform plans cannot verify actual Google API authorization or execute Workflows' server-side expression compiler.
