# Architecture and provisioning

## Configuration to execution

1. `config/defaults.yaml` supplies shared settings.
2. `config/environments/<environment>.yaml` overrides those settings.
3. `shared/configuration` merges mappings, replaces lists/scalars, rejects unknown fields and duplicate YAML keys, and validates cross-resource references.
4. `gcp-platform render` writes the resolved configuration, its SHA-256 hash, and an optional release manifest to Terraform variables.
5. Terraform provisions resources, then constructs `local.specs` in `infrastructure/environments/orchestration.tf` using **actual Terraform resource outputs**.
6. Each Workflows resource receives its own launch specification in the `WORKLOAD_SPEC` environment variable. This specification contains references and non-secret configuration, never secret payloads.
7. Scheduled and manual executions use the same workflow. Runtime arguments add a date window and run ID without replacing the resource specification.

Changing an unsupported YAML key fails validation. A new product or new job option needs both a schema change and a concrete implementation. YAML is not an unrestricted passthrough to arbitrary Google API fields.

## What Terraform provisions for Dataflow

Dataflow is a managed execution service. There is no always-running "dev Dataflow instance" to create.

Terraform enables APIs and provisions a dedicated worker service account, IAM grants, private subnet, Google API access, staging/temp bucket, input/output buckets, artifact repository, optional data stores, and a workflow capable of launching a Flex Template. It also provisions a Cloud Scheduler job when that workload's schedule is enabled.

At execution time the workflow calls `projects.locations.flexTemplates.launch`. Its launch request specifies:

- `containerSpecGcsPath`: a versioned Flex Template JSON object in the environment's artifact bucket.
- `parameters.sdk_container_image`: the digest-pinned worker image from the release manifest.
- `environment.serviceAccountEmail`: `module.iam.accounts.dataflow`.
- `environment.subnetwork`: the actual subnet self-link, with private worker IPs.
- `environment.machineType`, `numWorkers`, `maxWorkers`, and `diskSizeGb`: resolved environment sizing.
- Staging/temp locations and labels identifying the environment, job, and configuration hash.
- Workload parameters: input/output prefixes, optional Secret Manager version, Bigtable names, date window, and run ID.

For example, dev uses `initial_workers: 1` and `max_workers: 3`; prod overrides these to 2 and 10. The mocked Terraform tests inspect the resulting API request fields, rather than merely checking that YAML contains these numbers.

Dataflow creates workers when the job starts and releases them when the batch finishes. We deliberately do not use `google_dataflow_flex_template_job` to own batch executions in Terraform state: applying infrastructure should not run yesterday's ETL again. That resource can be appropriate for a separately designed long-lived streaming deployment, including its update/drain lifecycle.

## What Terraform provisions for Dataproc

This starter uses **Dataproc Serverless for Apache Spark**. Terraform provisions its service account, network access, artifact and staging locations, data permissions, workflow and schedule. It does not provision `google_dataproc_cluster`.

The workflow calls the Dataproc Batches API with:

- `pysparkBatch.mainPythonFileUri` and `pythonFileUris`: immutable driver/archive objects published from the release.
- `pysparkBatch.args`: the same data references and runtime date arguments used by the job contract.
- `runtimeConfig.containerImage`: a digest-pinned container with Python dependencies already installed.
- `runtimeConfig.version`: the configured supported runtime, initially `2.2`.
- Executor cores, initial/minimum executors, and maximum executors from YAML.
- `environmentConfig.executionConfig`: dedicated runtime service account, subnet, staging bucket, and TTL.

Dataproc creates managed execution resources for each batch. The template does not install Spark or Java in the custom image; the service supplies them. Spark jobs write Parquet to run-specific paths.

If a workload needs persistent clusters, Hive services, custom initialization actions, or non-Spark Hadoop components, add a separate cluster module and a separate submission adapter. Do not label the current `dataproc` settings as cluster settings: they are serverless settings.

## Other resources

Cloud Storage has separate raw, curated, staging, artifacts, and control buckets. Public access is prohibited and uniform bucket IAM is enabled. Staging files expire after seven days; control/run-claim objects have no expiry because they prevent accidental replay. Nonempty buckets are not force-deleted.

BigQuery has an environment-specific dataset and runtime permissions. The included pipelines currently use Cloud Storage and Bigtable sinks; no unimplemented BigQuery example is advertised.

Bigtable is disabled by default. Enabling it provisions an autoscaling cluster, instance, configured table and column family, and a batch application profile. Its names reach the Beam job via Terraform outputs. Instance deletion protection is enabled. The single-cluster template is not a multi-region availability design; introduce replication based on actual availability requirements.

Secret Manager resources are secret **containers** and access grants. An authorized secret operator adds versions outside Terraform. Configuration points to a numeric version, which the runtime identity retrieves during execution.

## Networking and isolation

Use a separate billing-enabled project and backend state per environment. Subnets use distinct RFC1918 ranges. Private Google Access is enabled, Dataflow public worker IPs are disabled, and serverless Spark uses the configured subnet. Internal worker traffic is allowed within that subnet.

External API examples require `network.enable_nat: true`, which creates a router and Cloud NAT. NAT provides outbound connectivity; it is not an egress allowlist. Add organization-specific egress controls, VPC Service Controls, CMEK, retention policies, and audit configuration where your requirements call for them.

## Reference documentation

- [Dataflow Flex Templates](https://docs.cloud.google.com/dataflow/docs/concepts/dataflow-templates)
- [Flex Template launch API](https://docs.cloud.google.com/dataflow/docs/reference/rest/v1b3/projects.locations.flexTemplates/launch)
- [Dataproc REST resources](https://docs.cloud.google.com/dataproc/docs/reference/rest)
- [Dataproc custom containers](https://docs.cloud.google.com/managed-spark/docs/guides/custom-containers)
- [Workflows monitoring](https://docs.cloud.google.com/workflows/docs/monitor)
