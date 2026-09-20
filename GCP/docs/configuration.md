# Configuration reference

## Overlays and validation

`defaults.yaml` plus exactly one environment file produces the deployment configuration. Mappings merge recursively. Lists replace completely. Scalars replace. `null` does not mean "delete this inherited job". Remove a shared job from defaults and define it only in the desired environments if it must be absent elsewhere. Optional jobs in `config/examples/partner-and-bigtable.yaml` are not automatically enabled.

Do not commit secret values or service-account key files. YAML can contain project IDs, group emails, service-account emails, resource sizes, schedules, and Secret Manager resource references.

The authoritative schema is `shared/configuration/models.py`. Generate its JSON Schema with `gcp-platform schema`; CI checks the committed schema for drift. Nested unknown fields, misspelled worker settings, duplicate YAML keys, invalid windows, unsupported use cases, missing secret grants, and API jobs without NAT fail before deployment.

## Environment fields

`environment`, `project_id`, and `region` identify the target. `name` provides a short naming prefix. The region must support your chosen services and machine types. Project existence, regional availability, subnet capacity, and service quotas are checked by real cloud deployment, not by local schema validation.

`network.subnet_cidr` is a private IPv4 range. `network.enable_nat` enables outbound internet access for API examples.

`access.deployment_service_account` names the bootstrap-created privileged CI identity. `developer_groups`, `operator_groups`, and `viewer_groups` contain group email addresses. See [security](security.md) for what each can do. Changing a list replaces its inherited contents.

`dataflow` controls machine type, initial/max workers, and worker disk size. `dataproc` controls the serverless runtime version, executor count limits, executor cores, and batch TTL. A workload also has `timeout_seconds` (default 14,400); Workflows requests cancellation if it exceeds this time. The Dataproc service TTL is an independent upper bound.

`bigtable` controls enablement, zone, node autoscaling bounds, CPU target, table, and column family. Disabling an already-created instance will require resolving deletion protection; do not disable a live database casually.

## Job definitions

Each key in `jobs` is a short job identifier, for example `clean-orders`. Supported pairs are:

- `dataflow` + `clean_orders`: partitioned JSONL → normalized, deduplicated JSONL.
- `dataflow` + `partner_extract`: authenticated HTTPS API → JSONL.
- `dataflow` + `bigtable_metrics`: partitioned orders → customer/day Bigtable totals and audit JSONL.
- `dataproc` + `daily_sales`: partitioned orders → daily aggregate Parquet.
- `dataproc` + `partner_extract`: executor-side authenticated API extraction → Parquet.

`input_prefix` and `output_prefix` are relative bucket prefixes ending in `/`. Terraform constructs the full `gs://` paths. The example input layout is `<input_prefix>/event_date=YYYY-MM-DD/*.jsonl`. Paths cannot use traversal or point at arbitrary buckets through YAML.

API examples require a `secret` key referencing `secrets`, an HTTPS `api_url`, and enabled NAT. The API contract is intentionally small: a GET request with a `date` parameter returns a JSON array of orders. Real pagination, quotas and authentication protocols vary by provider.

## Secret example

```yaml
secrets:
  partner:
    secret_id: partner-api-key
    version: '3'
    readers: [dataflow, dataproc]
jobs:
  beam-partner:
    engine: dataflow
    use_case: partner_extract
    secret: partner
    api_url: https://api.example.com/orders
    output_prefix: partner/
```

Terraform creates the container if needed and grants access to the specified runtime identities. The secret value is not created by this YAML. The numeric version must already contain an enabled secret version before launching the job.

## Production schedule example

```yaml
jobs:
  clean-orders:
    timeout_seconds: 14400
    schedule:
      enabled: true
      cron: '0 2 * * *'
      timezone: UTC
```

This fires at 02:00 UTC and processes the previous UTC calendar day. `timezone` affects the trigger time only, not the data partition timezone. Use one daily schedule per job with this window policy. Hourly schedules would repeatedly claim the same daily run ID. The validator checks five cron fields; Google validates full cron syntax at apply time.

Change code, config, or schema through a pull request. Apply a reviewed plan with the existing or new release manifest to make configuration changes effective; editing YAML alone does not update a running cloud job. Already-running jobs retain their original arguments.
