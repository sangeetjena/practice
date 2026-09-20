# Where to change what

Use this as the maintenance index for [the setup runbook](setup-runbook.md). Paths are relative to `GCP` unless stated otherwise. Source configuration is YAML, but only fields declared in `shared/configuration/models.py` are supported. Some infrastructure policy is intentionally encoded in Terraform or renderer code; adding an arbitrary YAML key will not configure it.

## Pick the scope first

Change `config/environments/dev.yaml`, `preprod.yaml` or `prod.yaml` for one environment. Change `config/defaults.yaml` only for a shared baseline. Environment values override shared values; nested mappings merge, lists replace. `config/examples/partner-and-bigtable.yaml` and `flink.yaml` are examples to merge into the intended overlay, not automatically loaded configuration.

Generated JSON schema, `build/ENV/platform.tfvars.json`, Terraform outputs, release manifests and Kubernetes YAML should not be hand-edited to establish lasting configuration. Update source, regenerate, review and deploy.

## Project, network and access

**Project, region and resource names:** edit `project_id`, `region`, `name` and `access.deployment_service_account` in the overlay. Trace consumers through `infrastructure/environments/main.tf` and each module. Changing project/name/region may replace resources; plan a migration and a new backend where appropriate. Existing state is not automatically moved by a YAML edit.

**Subnet and outbound internet:** edit `network.subnet_cidr` and `network.enable_nat`. Implemented by `infrastructure/modules/networking/main.tf`. External API examples and the configured GKE public-image path require NAT. Firewall policy, Private Google Access and router/NAT details are module code; they are not separately exposed YAML options.

**Who can view or run jobs:** edit `access.developer_groups`, `operator_groups`, `viewer_groups`. These lists contain emails without `group:`. `modules/iam/main.tf` implements permissions: developers invoke only in dev; operators invoke where configured; viewers inspect jobs/logs. These groups are not project editors or Kubernetes administrators. Bucket data access and GKE namespace access need separately reviewed grants.

**Who can modify infrastructure or deploy:** configure GitHub protections and bootstrap federation inputs in `infrastructure/bootstrap/main.tf` / a private `bootstrap.tfvars` copied from the example. Numeric repository/owner IDs, release branch and protected environment subject define trust. Bootstrap `enable_flink` adds GKE provisioning permission. This is distinct from platform YAML and runtime workload accounts.

**Which account runs a batch job:** the current engine accounts are generated in `modules/iam/main.tf`; `infrastructure/environments/orchestration.tf` attaches them to launch specifications. YAML identifies the deployer but does not expose a per-job worker-account override. Per-job isolation requires an IAM/account-map design change plus orchestration and tests.

## Dataflow and Dataproc

**Dataflow capacity:** edit `dataflow.machine_type`, `initial_workers`, `max_workers`, `disk_size_gb`. They apply to subsequent launches through `orchestration.tf`. There is no permanent Dataflow instance to resize. To support per-job rather than per-engine capacity, add a schema contract and explicit per-job launch mapping.

**Dataproc capacity/runtime:** edit `dataproc.runtime_version`, `executor_instances`, `max_executors`, `executor_cores`, `ttl`. These affect serverless batch requests. `ttl` is a service-side upper bound; `jobs.JOB.timeout_seconds` separately controls workflow cancellation. Custom Spark properties, driver sizing or persistent clusters are not currently YAML options.

**Input/output locations:** edit `jobs.JOB.input_prefix` / `output_prefix`. They are relative bucket prefixes ending with `/`, not arbitrary `gs://` URIs. Actual buckets come from Terraform. Schema, transformation and deduplication behavior live in `jobs/dataflow/main.py`, `jobs/dataproc/main.py`, and `shared/runtime.py`; changing a prefix does not change the record contract.

**Add another job using an implemented use case:** add a uniquely named entry to `jobs` in the selected overlay, specify a supported engine/use-case pair and output prefix, validate, render with the existing release and apply. Terraform creates its workflow and optional schedule. Existing code can be reused without a new image only if that published release already implements the use case.

**Add a new transformation:** implement the engine branch, extend `Job.use_case` and supported-pair validation in `models.py`, update parsers/Flex metadata as needed, test fixtures and expected results, regenerate schema, publish a new release and deploy it. Do not assume adding a job name makes an unknown use case executable.

**Add an externally supplied argument:** update `tooling/cli.py`, the allowlist/type checks and launch mapping in `orchestration/batch.yaml`, both relevant job parsers and Dataflow metadata. Add boundary tests and document semantics. Keep service accounts, resource privileges, API endpoints and secret values out of untrusted runtime overrides.

## Secrets, storage and databases

**API integration:** merge the partner example; set `jobs.JOB.secret`, `api_url`, `secrets.ALIAS.secret_id`, `version`, `readers`, and NAT. Only HTTPS API examples use these fields. Runtime fetching is in `shared/authentication/secrets.py` and each engine's worker/executor code. Pagination and provider-wide rate limiting need code changes.

**Secret rotation:** add the value through Secret Manager under an authorized identity, update the numeric YAML version, apply using the current release and validate a new run. `modules/secret_manager` owns containers/grants only. Never implement rotation by committing a payload or putting it in Terraform variables.

**Storage retention/naming/access:** edit `modules/storage/main.tf`. There are five platform buckets: raw, curated, staging, artifacts and control. Staging has a seven-day cleanup rule; claim objects are retained. Retention days, CMEK, location topology and per-job buckets are not exposed as YAML fields. Add typed fields plus module wiring if these need to vary by environment.

**BigQuery dataset/tables:** `modules/bigquery/main.tf` provisions the dataset and roles; `name`/environment determine its name and `region` its location. No current example writes BigQuery, and table schemas are not configurable YAML. Implement tables and a job sink before promising that behavior.

**Bigtable:** edit `bigtable.enabled`, `zone`, `min_nodes`, `max_nodes`, `cpu_target`, `table`, `column_family`, and enable a `dataflow/bigtable_metrics` job. The Terraform module owns instance/table/profile infrastructure; Beam code owns row keys, values and deterministic write timestamps. Node sizing is configuration; a new row-key design is a data migration. Disabling a live instance is not a routine feature toggle because deletion protection/data retention must be addressed.

## Batch orchestration and alerts

**Trigger time:** edit `jobs.JOB.schedule.enabled`, `cron`, `timezone`. `orchestration.tf` creates Cloud Scheduler and `orchestration/batch.yaml` handles execution. The current window is always the previous UTC day. Local-calendar windows, hourly partitions, catch-up and dependency DAGs require orchestration changes; two cron offsets create no dependency.

**Backfill dates:** pass `--start-date`, `--end-date`, `--run-id` to the CLI instead of editing YAML. Preview first; `--execute` submits. Claims are per job/run ID, and outputs are isolated by run. See [operations](operations.md) before retrying failures or overlapping windows.

**Timeout/polling/retry behavior:** set job `timeout_seconds` for the supported limit. Poll intervals, GET retry behavior, claim handling and launch/cancel logic live in `orchestration/batch.yaml`. Review changes for ambiguous launch responses and orphaned engine jobs.

**Alert destinations:** the failed-workflow policy is defined in `infrastructure/environments/orchestration.tf`. It initially has no notification channels. Add reviewed notification-channel resources/references and policy wiring there, or expose a typed setting if required. There is no existing `alerts:` YAML setting. Missing-run detection and Flink alert rules require additional monitoring configuration beyond the current metrics collection.

## Flink/GKE

**Enable and connect:** edit `flink.enabled`, `namespace`, `authorized_cidrs`, `pod_cidr`, `service_cidr`, `master_cidr`, and `network.enable_nat`; provision using `modules/gke/main.tf`. Replace documentation CIDRs. Bootstrap also needs `enable_flink=true`. Namespace changes affect identity bindings, RBAC and application resources; plan their migration.

**Cluster capacity:** edit `flink.node_machine_type`, `min_nodes`, `max_nodes`. Node disk size, release channel and deletion protection currently live in the GKE Terraform module. GKE node capacity and Flink task slots are separate limits.

**Application resources:** edit `parallelism`, `task_slots`, `jobmanager_cpu`, `taskmanager_cpu`, `jobmanager_memory`, `taskmanager_memory`, `jobmanager_replicas`, `rocksdb_local_disk_gb` under `flink`. They are rendered by `tooling/flink.py`. Check actual Kubernetes scheduling and Flink memory validation; syntactically valid YAML does not guarantee enough node resources.

**Join/window timing:** edit `join_horizon_seconds`, `allowed_lateness_seconds`, `out_of_orderness_seconds`, `idle_timeout_seconds`, `max_retention_seconds`, `window_seconds`, `file_discovery_seconds`. Renderer converts them to `job.args`; `JoinJob.java` and `DelayedJoin.java` consume them. Retention must cover horizon plus lateness. Review state size, late-event behavior and stateful upgrade implications, not only schema validity.

**Checkpoints and state:** edit `checkpoint_interval_seconds` / `checkpoint_timeout_seconds`. Backend type, incremental mode, retained checkpoints and savepoint/HA layout are in `tooling/flink.py`. Bucket permissions/protection are in the GKE module. Java state names/serializers and operator UIDs are code contracts; schema changes may prevent restore. Never add age-based deletion of shared SST files without a correct checkpoint-aware cleanup design.

**Flink schedule/backfill:** `flink.batch_schedule` and `batch_timeout_seconds` configure the bounded CronJob. `jobs/flink/submitter/submit.py` chooses dates, creates and watches its FlinkDeployment. `tooling.flink render --start-date ... --end-date ... --run-id ...` creates an explicit bounded run. Both sources' partition dates must include the desired counterparts. Suspended/removed schedules and completed CR cleanup require explicit Kubernetes operations as documented in the Flink runbook.

**Images/operator/plugins:** edit `jobs/flink/pom.xml`, Dockerfile and the pinned operator installation procedure together. `tooling/flink.py` declares `flinkVersion`; update it when changing major/minor compatibility. Match GCS and Prometheus plugin versions to the Flink runtime, run Maven tests, build/publish, then rehearse savepoint recovery in preprod.

**Metrics/logging:** custom join metrics are in `DelayedJoin.java`, logger configuration in `jobs/flink/log4j-console.properties`, reporter and PodMonitoring in `tooling/flink.py`, GKE collection in `modules/gke/main.tf`. Configure notification rules separately. Distributed tracing is not implemented.

## Full change workflow

1. Identify whether the change is environment configuration, infrastructure policy, job code, schema, or CI. Find the source above.
2. Edit the source and add/update meaningful tests when behavior changes. Regenerate JSON schema for model changes.
3. Validate affected overlays; run relevant Python/Java tests, Terraform formatting/validation/mock plans when infrastructure changes.
4. Publish a new immutable release for executable changes. For configuration-only batch changes, retain the existing release manifest.
5. Select the correct environment backend, render, save/review/apply the plan, export fresh outputs. For Flink, additionally render/review/apply Kubernetes resources with the correct Flink release.
6. Run the appropriate dev smoke/recovery test, promote artifacts, and repeat environment-specific checks before production.
7. Record Git revision, image digests, config hash, plan, outputs location, execution IDs and validation evidence in the handover record.

No supported setting should stop at the schema: trace every new field through its Terraform or manifest consumer and into runtime behavior, then test that changing the value changes the intended resource or request.
