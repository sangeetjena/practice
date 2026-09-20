# GCP data engineering template

A YAML-configured platform for **Dataflow Flex Templates**, **Dataproc Serverless PySpark**, optional **Bigtable** and **Flink on GKE**, Cloud Storage, BigQuery, Secret Manager, and scheduled batch execution using **Cloud Scheduler → Workflows**.

The repository is a deployable starter, not an already deployed cloud platform. Replace the example project IDs and configure your identities before using cloud commands. Billing-enabled GCP projects must already exist. Local tests do not prove that your organization's IAM policies, quotas, regions, and network policies permit a deployment.

## Start here

- [Setup and implementation runbook](docs/setup-runbook.md): ordered steps to reproduce the project and onboard another engineer.
- [Where to change what](docs/change-guide.md): source files, YAML settings, infrastructure policy, and the deployment steps for each change.
- [Flink runbook](docs/flink.md): GKE, Docker, two-source joins, checkpoints, scheduling, and telemetry.
- [Architecture and resource provisioning](docs/architecture.md): what Terraform creates, and how dev/prod resource settings reach each job.
- [Deployment guide](docs/deployment.md): bootstrap, build, publish, promote, and deploy.
- [Configuration reference](docs/configuration.md): overlays, resources, users, and job settings.
- [Security and runtime secrets](docs/security.md): deployer versus worker identities, Secret Manager, and federation.
- [Scheduling, backfills, and operations](docs/operations.md): schedules, external arguments, retries, failure monitoring, and output semantics.
- [Working examples](jobs/README.md): Beam and PySpark use cases, local commands, and sample data.
- [Tool choices](docs/tooling.md): Terraform, Python, Docker, CI, Gradle, Bazel, Make, Workflows, and Composer.

## Directory map

```text
config/                  defaults + dev/preprod/prod overlays + generated JSON schema
infrastructure/bootstrap administrator-run state bucket and GitHub federation bootstrap
infrastructure/environments one reusable Terraform root, separate state per environment
infrastructure/modules/  IAM, network, storage, registry, BigQuery, Bigtable, secrets
orchestration/batch.yaml shared launch/wait/cancel workflow deployed once per configured job
jobs/dataflow/           order cleansing, API extraction, Bigtable customer-day metrics
jobs/dataproc/           daily sales aggregation, API extraction
jobs/flink/              Java stateful order/payment join and scheduled batch submitter
jobs/fixtures/           small JSONL input partitions
shared/                  configuration validation, runtime contracts, secret access
tooling/                 cross-platform CLI, packaging, publication, promotion
requirements/            pinned dependency sets for containers and CI
tests/                   configuration, workload, security-boundary, and contract tests
```

GitHub workflows are in the **practice repository root** at `.github/workflows/gcp-checks.yml` and `.github/workflows/gcp-deploy.yml`.

## Local setup (PowerShell)

From `practice/GCP`, use Python 3.11 to match the runtime containers:

```powershell
uv venv --python 3.11 .venv
.venv/Scripts/python.exe -m ensurepip
.venv/Scripts/python.exe -m pip install -r requirements/dev.lock
.venv/Scripts/python.exe -m pip install -e . --no-deps
.venv/Scripts/python.exe -m tooling.cli validate --env dev
.venv/Scripts/python.exe -m tooling.cli validate --env preprod
.venv/Scripts/python.exe -m tooling.cli validate --env prod
.venv/Scripts/python.exe -m tooling.cli render --env dev
.venv/Scripts/python.exe -m pytest -q
```

Use `gcp-platform` after activating the virtual environment. On Linux, use `.venv/bin/python`. Install `requirements/beam.lock` for Beam local runs and `pyspark==3.5.3` plus Java 17 for Spark tests. CI runs both engines on Linux; tests for engines not installed locally are explicitly skipped.

Rendering produces `build/dev/platform.tfvars.json`. It does **not** contact GCP. Ordinary Terraform plans and applies are separate, explicit commands.

## What changes between environments?

Dev starts Dataflow with 1 worker and caps it at 3; prod starts with 2 and caps it at 10. Spark max executors are 4 in dev and 10 in prod. Each environment resolves its own project, buckets, subnet, service accounts, secret references, artifact registry, workflows, and Terraform state. Prod schedules are enabled in YAML but remain paused until a release manifest is deployed.

Terraform provisions the **platform around Dataflow**, not a permanent Dataflow VM instance. Workflows launches an individual Dataflow job; Dataflow provisions its workers for that run. Dataproc follows the same pattern using serverless batches. [Read the full lifecycle](docs/architecture.md).

## Backfill example

After deployment, save Terraform outputs as described in the deployment guide:

```powershell
gcp-platform run clean-orders --env dev --outputs build/dev/outputs.json --start-date 2026-09-01 --end-date 2026-09-20 --run-id bf-sept-v1
```

This previews the exact Workflows execution request. Add `--execute` to submit it. The end date is exclusive. Resource settings and secret values cannot be overridden through these arguments.

## Scope

Included: reusable infrastructure, five workload/engine combinations, immutable artifact publication/promotion, three environments, protected CI integration, runtime secret references, independent scheduled workflows, bounded execution monitoring, and safe run-specific output paths.

Not included: organization/project creation, a persistent Hadoop cluster, CDC connectors, a Composer environment, an automatic data-catalog publication step, or a multi-job dependency DAG. Cron offsets are not dependency management. Extend Workflows with explicit child workflow calls when one job must wait for another; use Composer when you need Airflow's DAG, sensor, and backfill management capabilities.
