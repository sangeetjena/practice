# Reproduce this project: setup and implementation runbook

This is the ordered record of how the template was assembled, followed by the procedure another engineer can repeat. It distinguishes repository implementation from cloud provisioning: the repository was created and tested locally; no GCP project was deployed during implementation.

## Reading order and completion status

Start with this document for installation and the complete lifecycle. Use [the configuration change guide](change-guide.md) to find the exact file and deployment path for a change. Consult [deployment](deployment.md) for bootstrap/promotion commands, [security](security.md) for identities and secrets, [operations](operations.md) for scheduling/retries, and [Flink](flink.md) for GKE-specific procedures.

The earlier implementation work is complete at the repository/local-validation level: Python and Beam checks passed, Terraform validation and mocked plans completed, and the deployment, rotation, promotion, scheduling and backfill guides were written. Real GCP provisioning, server-side Workflows validation, Docker builds and cloud smoke/recovery tests remain outstanding. Example project IDs are intentionally still placeholders. Local success is not a production deployment sign-off.

All shell examples below start in `practice/GCP` unless specified otherwise. They use PowerShell. After activating the Python environment, `gcp-platform` and `python -m tooling.cli` are equivalent. In Linux CI, use `.venv/bin/python` and `source .venv/bin/activate` instead of Windows paths. Stop on a failed command and resolve it before continuing to the next lifecycle stage.

## Prerequisites and ownership

Use the `practice` repository and work inside `GCP`. Decide the dev, preprod and prod project IDs, supported region, GitHub repository/owner IDs, release branch, developer/operator groups, billing owner, data contract and production approvers. Use separate projects and Terraform state for each environment.

Install Python 3.11, uv, Terraform, Google Cloud CLI and Docker. For the Flink extension, also install Java 17, Maven, Helm, kubectl and the GKE auth plugin. Linux CI is the supported container/build environment; the configuration CLI also works on Windows.

### Decisions to collect before cloud setup

- Existing billing-enabled GCP project IDs for dev, preprod and prod, supported region, quota owner and administrator contact. This template does not create organizations, projects or billing accounts.
- A private subnet CIDR and, for Flink, non-overlapping pod/service/master ranges plus the administrator/runner's actual public egress CIDR.
- GitHub repository name, immutable numeric repository/owner IDs, trusted release branch, protected environment reviewers and deployment service-account name. The bootstrap example uses `master`; change it if the actual release branch differs.
- Developer/operator/viewer group emails, input-data owner, secret operator and alert recipients. Empty groups grant no human access.
- Input contract, expected daily arrival time, UTC partition policy, resource budget, and whether Bigtable, external API examples or Flink should be enabled.
- For API examples: the controlled HTTPS endpoint, secret ID and enabled numeric version. For Flink CI: a self-hosted Linux runner on an allowed network with the `gcp-deploy` label.

### Install the local tools

Use your team's approved installers. The versions below match this repository's validation baseline; they are not a claim that these are the newest available versions.

1. Install Git and clone the practice repository, or use your existing checkout. Run `git status --short` before editing so unrelated local changes are visible.
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/). It can install the Python 3.11 runtime used below. A separately installed Python 3.11 also works.
3. Install [Terraform](https://docs.hashicorp.com/terraform/install), preferably 1.11.4 to match CI. The configuration requires at least 1.9. Provider versions are selected by the checked-in `.terraform.lock.hcl` files, currently Google/Google Beta 6.50.0. Do not run `init -upgrade` as an incidental setup step.
4. Install [Google Cloud CLI](https://docs.cloud.google.com/sdk/docs/install) for cloud operations. CLI sign-in and Application Default Credentials are separate; both are explained below.
5. Install [Docker Desktop with Linux containers](https://docs.docker.com/desktop/setup/install/windows-install/) on Windows, including its documented WSL/virtualization prerequisites. Start the daemon. Having `docker.exe` on PATH alone is insufficient.
6. For Flink and Spark validation, install a Java 17 JDK and set `JAVA_HOME` to its root, with its `bin` directory on PATH. Install Maven 3.9.9 for Flink. See [Adoptium](https://adoptium.net/installation/) and [Maven installation](https://maven.apache.org/install.html).
7. For GKE deployment, install Helm, kubectl and `gke-gcloud-auth-plugin`. Follow [GKE cluster access setup](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl). SDK-managed installations can use `gcloud components install kubectl gke-gcloud-auth-plugin`; package-managed SDK installations use their corresponding package manager. Install Helm using [its installation guide](https://helm.sh/docs/intro/install/).

Verify the tools needed for your chosen scope:

```powershell
git --version
uv --version
terraform version
gcloud version
docker version
docker info
java -version
mvn -version
kubectl version --client
gke-gcloud-auth-plugin --version
helm version
```

Configuration validation and Python tests need no GCP account. Maven unit tests need no cluster. Terraform provider initialization and dependency installation need download access; Terraform mock plans do not need cloud credentials. Docker publication and real Terraform apply do need cloud authentication and permissions.

### Create the Python environment

```powershell
Set-Location C:\path\to\practice\GCP
uv venv --python 3.11 .venv
.venv/Scripts/python.exe -m ensurepip
.venv/Scripts/python.exe -m pip install -r requirements/dev.lock -r requirements/beam.lock
.venv/Scripts/python.exe -m pip install -e . --no-deps
.venv/Scripts/Activate.ps1
python --version
gcp-platform --help
```

`requirements/dev.lock` installs validation/testing/CLI cloud dependencies. `beam.lock` adds the Beam SDK and its Google integrations. `cloud.lock` is the smaller cloud-runtime set used by the Spark image. `pyproject.toml` defines direct requirements, package discovery and the CLI entry point; the lock files pin their resolved dependencies. Editable installation makes local source changes visible without reinstalling the project.

If activation is blocked by a workstation policy, use `.venv/Scripts/python.exe -m tooling.cli ...`, `.venv/Scripts/python.exe -m pytest ...`, and `.venv/Scripts/ruff.exe ...` directly. Do not change organization-wide PowerShell policy to run this project.

For full Spark testing, use the supported Linux/CI environment with Java 17 and run `python -m pip install pyspark==3.5.3`. Without PySpark, the Spark test module is skipped. Native Windows Spark may require additional Hadoop setup; a skipped test is not Spark validation.

### Authenticate when moving from local work to cloud work

```powershell
gcloud auth login
gcloud auth application-default login
gcloud auth list
```

The first login serves `gcloud` commands. ADC serves Terraform and Python Google clients. They can represent different users, so confirm the intended identity before planning or publishing. Use explicit projects/backends and Terraform outputs rather than relying on the CLI's default project. Approved service-account impersonation needs a separately granted impersonation permission. CI uses GitHub federation, not these interactive logins or exported JSON keys. See [Google's authentication guide](https://docs.cloud.google.com/sdk/docs/authenticate).

Bootstrap must run under an authorized administrator. Provisioning IAM, enabling services and creating federation requires broader rights than invoking a data job. A developer who can run a dev workflow is not automatically a bootstrap administrator or artifact publisher.

## Steps used to create the template

1. **Inspect the repository.** Check existing instructions, Git status and CI conventions. The existing repository already used GitHub Actions. Keep unrelated projects unchanged.
2. **Choose the tools and execution model.** Use Terraform for persistent infrastructure, Python for Beam/PySpark and configuration tooling, Docker for runtime dependencies, and Scheduler plus Workflows for batch orchestration. Keep batch execution out of Terraform resource lifecycle.
3. **Create the folder structure.** Add `config`, `infrastructure`, `orchestration`, `jobs`, `shared`, `tooling`, `requirements`, `tests` and `docs`. Ignore virtual environments, build outputs, Terraform state/plans, credentials and caches.
4. **Define the configuration contract first.** Implement strict Pydantic models, duplicate-key rejection, deterministic YAML overlays and configuration hashing. Add dev/preprod/prod overlays and a generated JSON Schema. Treat a new YAML option as incomplete until a concrete resource or job consumes it.
5. **Implement the administrator bootstrap.** Create the versioned Terraform state bucket, dedicated deployer and repository/branch/environment-restricted GitHub federation. Generate no service-account keys.
6. **Implement Terraform modules.** Add API enablement, service agents, runtime identities, private networking, buckets, registry, BigQuery, optional Bigtable, and Secret Manager containers/IAM. Use non-authoritative IAM member resources to avoid replacing unrelated bindings.
7. **Connect resources to runtime requests.** Build Workflows launch specifications using Terraform outputs for actual resource names. Copy worker/executor sizing from resolved YAML. Keep secret payloads out of Terraform and workflow state.
8. **Implement the workloads.** Add Beam order cleansing, Beam/PySpark API extraction, Spark daily sales, and Bigtable metrics. Use a shared date/record contract and fixed test fixtures. Fetch secrets on workers/executors using attached identities.
9. **Implement orchestration.** Add argument validation, date windows, atomic run claims, launch, polling, terminal failure handling and cancellation. Add configurable cron triggers with schedules paused until a release exists.
10. **Implement build and promotion tooling.** Package shared Python code deterministically, build runtime images, pin pushed digests, publish immutable release paths, and promote existing artifacts without rebuilding their code.
11. **Implement CI and documentation.** Add path-scoped GitHub checks/deployment workflows and guides for architecture, security, configuration, operations, examples and deployment.
12. **Validate locally.** Resolve dependency locks, run Ruff, Python tests and Beam DirectRunner tests; initialize Terraform providers, run formatting/validation and credential-free mocked dev/prod plans. Fix schema/API mismatches exposed by those checks. CI additionally runs Spark with Java installed.
13. **Extend for Flink.** Add optional GKE infrastructure, a separate Java/Maven Flink image, operator-managed Kubernetes resources, strict YAML arguments, keyed join state, watermark/window handling, RocksDB checkpointing and managed Prometheus telemetry. Follow the dedicated [Flink runbook](flink.md).

### Implementation details and corrections recorded during validation

The initial environment was assembled locally in ignored `.venv` and `.cache` directories. Python 3.11.13, Terraform 1.11.4, Java 17 and Maven 3.9.9 were used. Downloaded Terraform/Maven distributions were checksum-verified. These directories are developer tools and caches, not deployment inputs; a new engineer should install the documented tools rather than depend on this workstation's cache paths.

Dependency resolution produced the committed universal Python lock files. Python tests exercised YAML overrides and validation, runtime date contracts, numeric secret references, deterministic packaging, Beam local execution and Flink manifest rendering. Terraform was initialized without a remote backend for schema validation and mock tests. Provider schema findings were corrected, including the project-scoped Workflows invocation grants documented in the security guide.

The Flink extension added state expiry and processing-time cleanup, snapshot/restore tests, and explicit timestamp/watermark propagation after matching. Java test compilation was corrected and Maven then produced the shaded JAR with all seven tests passing. The rendered pods received filesystem group 999 so the Flink user can write the RocksDB volume. GKE resource dependencies were made explicit around identities and node permissions, and the optional GKE/Bigtable Terraform plan was added to the tests.

The Flink CI connection command was changed to module invocation (`python -m tooling.connect_gke`) so imports resolve consistently. Docker availability was checked; the local Linux engine pipe was absent, so images were not built or pushed. No credentials, real project IDs or secret payloads were added, and no Terraform apply or cloud job submission was performed. The ordered steps above describe the reproducible implementation process, not a claim that every illustrative cloud command was executed.

## Understand the project before changing it

### Source files versus generated files

`config/defaults.yaml` is the shared baseline. `config/environments/dev.yaml`, `preprod.yaml`, and `prod.yaml` contain environment overrides. `config/examples/*.yaml` are copy/merge examples only; the loader never automatically imports them. Some defaults, particularly Flink settings, live in the Pydantic models even when omitted from YAML.

`shared/configuration/models.py` is the authoritative schema and validation logic. `loader.py` merges defaults with exactly one environment overlay, rejects duplicate keys, validates the result, and computes a deterministic SHA-256 configuration fingerprint. `config/schema/platform.schema.json` is generated for editors/CI. Change the Python model first and run `gcp-platform schema`; do not hand-edit the generated schema.

`tooling/cli.py` renders `build/ENV/platform.tfvars.json`, packages code, builds/publishes/promotes releases and previews/submits workflow requests. Terraform outputs are exported to `build/ENV/outputs.json`; the CLI checks that their environment and configuration hash match the selected source configuration. After a configuration apply, export outputs again before publication or job submission.

`build/`, `.cache/`, `.venv/`, `target/`, Terraform local state/plans and credential files are ignored. Generated files are not the source of truth for future edits. Release manifests and plans still need appropriate retention in artifact storage/CI; ignored does not mean disposable. Back up bootstrap state securely.

### How YAML becomes a running job

1. The loader resolves defaults plus the selected overlay and validates types and references.
2. `render` writes Terraform variables containing that configuration, its hash, and an optional release manifest.
3. Terraform creates/updates resources and builds launch specifications from the resolved settings and actual resource outputs. `infrastructure/environments/orchestration.tf` connects them to the shared workflow definition.
4. A release manifest supplies immutable image digests, Flex Template location and Spark code/archive locations. Configuration does not contain executable image builds.
5. Scheduler or an operator invokes Workflows. It combines approved deployment settings with the allowed date/run arguments and launches the engine.
6. The service attaches the configured runtime identity; worker/executor code reads secret versions at runtime. Arguments contain references, never secret payloads.
7. Flink uses a parallel route: `tooling/flink.py` combines the same resolved configuration with Terraform outputs and its own release manifest to render Kubernetes resources. Applying those resources lets the operator start/update the application.

An edit to YAML alone changes no cloud resource. A Terraform apply updates infrastructure and batch launch specifications. A Flink render plus Kubernetes apply updates its application configuration. Already-running batch jobs keep their original launch arguments; a Flink application update can trigger a stateful upgrade.

### Infrastructure inventory and ownership

- `infrastructure/bootstrap/main.tf`: administrator-owned state bucket, deployment account, GitHub federation and provisioning permissions. Its variables are separate from platform YAML.
- `infrastructure/environments/main.tf`: enables APIs, creates service agents and connects modules. `variables.tf` defines root inputs, `versions.tf` providers/backend, `outputs.tf` the CLI handoff, and `orchestration.tf` workflows/schedules/monitoring. Both roots have provider lock files.
- `modules/iam`: engine, workflow and scheduler identities; human groups; launch and impersonation permissions. Runtime identities are shared per engine/environment, not per job.
- `modules/networking`: VPC/subnet, private Google access, required worker network rules and optional NAT. GKE secondary address ranges are added when enabled.
- `modules/storage`: `raw` inputs, `curated` outputs, `staging` temporary engine files, `artifacts` immutable releases and `control` run claims. Buckets use uniform access, public access prevention and versioning. Only staging has the implemented seven-day age cleanup rule.
- `modules/artifact_registry`: Docker repository and access grants, with immutable release tags.
- `modules/bigquery`: analytics dataset and runtime permissions. Current example jobs do not populate BigQuery; a sink must be implemented to use it.
- `modules/bigtable`: optional instance/cluster, autoscaling, table/family and batch app profile. Enabling an API does not mean an instance exists.
- `modules/secret_manager`: secret containers and runtime access grants. It does not create secret values.
- `modules/gke`: optional private-node regional cluster, node pool, node/runtime identities, Workload Identity and protected checkpoint storage. Cluster and checkpoint-bucket deletion protections are explicit in this module.

Dataflow has no permanent VM instance in this template: each Flex Template launch provisions a managed job's workers. Dataproc uses serverless batches, not a persistent Hadoop cluster. GKE, Bigtable (if enabled), NAT and stored data can incur costs even when batch jobs are idle. Terraform state records ownership and resource addresses; it is not job output or a runtime configuration distribution service.

### Job code and orchestration ownership

`jobs/dataflow/main.py` implements Beam cleansing, API extraction and Bigtable metrics. `jobs/dataproc/main.py` implements Spark aggregation and API extraction. `shared/runtime.py` defines common date/data/API behavior and `shared/authentication/secrets.py` reads Secret Manager using ADC. Each engine's Dockerfile defines its runtime, while Dataflow's `metadata.json` describes Flex Template parameters.

`jobs/flink/src/main/java/example/platform` contains event parsing, keyed joining, timestamp propagation and window aggregation. Its `pom.xml` owns Java dependencies/tests; Dockerfile owns the Flink runtime/plugins; `jobs/flink/submitter` creates and watches bounded runs. `tooling/flink.py` owns operator manifests, RBAC, monitoring and scheduling configuration. `tooling/connect_gke.py` connects using Terraform outputs.

`orchestration/batch.yaml` is executable Google Workflows source, not an environment overlay. It owns date validation, claims, launch, polling and cancellation. The three `.github/workflows/gcp-*.yml` files are in the practice repository root and define CI validation, batch platform deployment and Flink deployment. Editing workflow YAML can change credentials, approval boundaries and deployment behavior; review it accordingly.

## Configure the first environment

Edit `config/environments/dev.yaml` with the actual project ID and bootstrap deployment-account email. Add real group emails without a `group:` prefix. Override `region`, `network` or engine sizing only where the environment differs. Keep `config/defaults.yaml` for intentional shared policy.

For example, changing only dev's Dataflow capacity is an overlay fragment:

```yaml
dataflow:
  initial_workers: 1
  max_workers: 2
```

Mappings merge recursively, so this inherits the existing machine type and disk size. Lists replace entirely; specifying one `operator_groups` entry replaces the inherited list. Duplicate YAML keys fail validation: merge example fragments into existing sections instead of appending another `jobs:` or `network:` key. `null` is not an inheritance-deletion operator.

Run the following and inspect the generated configuration without modifying it:

```powershell
gcp-platform validate --env dev
gcp-platform validate --env preprod
gcp-platform validate --env prod
gcp-platform render --env dev
Get-Content build/dev/platform.tfvars.json
```

Placeholder IDs can pass syntactic validation; this command does not verify project existence, billing, organizational policies or quotas. Publication rejects placeholder IDs. Review all environments before actual deployment.

## Repeatable implementation checkpoints

After editing configuration models:

```powershell
gcp-platform schema
gcp-platform validate --env dev
gcp-platform validate --env preprod
gcp-platform validate --env prod
```

After editing Python workloads or deployment tooling:

```powershell
ruff check jobs shared tooling tests
pytest -q
gcp-platform package --version local-check
```

After editing Terraform:

```powershell
gcp-platform render --env dev
gcp-platform render --env prod
terraform fmt -check -recursive infrastructure
terraform -chdir=infrastructure/bootstrap init -backend=false
terraform -chdir=infrastructure/bootstrap validate
terraform -chdir=infrastructure/environments init -backend=false
terraform -chdir=infrastructure/environments validate
terraform -chdir=infrastructure/environments test
```

`-backend=false` and mocked providers perform local validation; they are not proof of a successful cloud deployment. Follow [deployment.md](deployment.md) for actual backend initialization and apply.

## First deployment sequence for a new engineer

1. Clone the reviewed repository revision and install its locked dependencies.
2. Fill real environment IDs, group emails, region and network ranges. Leave optional services off until needed.
3. Have an administrator bootstrap each project and protect the GitHub environments/branch.
4. Render and review a dev infrastructure plan; apply with dev's backend and export outputs.
5. Populate fixture input and any required Secret Manager versions using authorized data/secret operators.
6. Publish one uniquely versioned artifact release, deploy it and run explicit fixture windows.
7. Verify output totals, runtime service accounts, network isolation, failure visibility and retry behavior.
8. Promote the same image digests/artifacts to preprod, apply preprod configuration and repeat smoke tests.
9. Apply the reviewed production release/configuration after approval. Confirm real input arrival and the schedule's UTC date policy before relying on it.
10. For Flink, follow the separate GKE/operator/image/deployment steps and verify checkpoint restore and delayed-key scenarios before production.

### Bootstrap and environment state: exact order

Use [deployment sections 2–3](deployment.md) for the full commands. First create and edit `build/dev/bootstrap.tfvars` from the example. Run bootstrap plan/apply with dev's explicit local state path. Preserve that state. If enabling Flink, add `enable_flink = true` to these bootstrap inputs; it is not a platform YAML key.

For platform resources, render YAML, choose an environment-specific `TF_DATA_DIR`, initialize its GCS backend, save/review the plan, apply that exact plan, then export JSON outputs. The state bucket created by bootstrap must exist before the environment backend can initialize. When deliberately changing an existing working directory to a different backend, use `init -reconfigure` with the intended bucket/prefix; never migrate dev state into prod as a shortcut. Prefer separate `TF_DATA_DIR` directories so their backend caches never mix.

Do not use `-backend=false` for real deployment; that mode is only for local validation. Do not run cloud commands against the ignored files produced by a mocked plan. A first apply without a release provisions foundations but leaves scheduled jobs paused and workflows unable to execute data jobs.

### Publish, smoke-test and promote

From the intended Git revision, run the checks, start Docker, publish a unique version, render with the resulting release manifest, and apply the release plan. Export outputs again. Follow [jobs/README.md](../jobs/README.md) to upload fixed fixtures and run explicit dates. Expect three cleaned rows and daily revenue totals of 2,000 and 500 cents. Validate runtime identity/network behavior as well as output values.

Promote the same artifacts to preprod and prod with the documented `promote` command; do not rebuild each environment. Cross-project artifact read permissions are an explicit administrator decision. Each target needs its own infrastructure, outputs and release manifest. The release version identifies code; configuration hashes identify environment settings. Record both.

### Configure CI and approvals

Create GitHub environments `gcp-dev`, `gcp-preprod`, `gcp-prod`, protect the trusted release branch and require production reviewers. Set `GCP_WIF_PROVIDER`, `GCP_DEPLOYER_SA`, `GCP_STATE_BUCKET`, and `GCP_ARTIFACT_BUCKET` in each environment as described in [deployment](deployment.md). These are references, not long-lived credentials. GitHub branch/environment protections are manual repository setup, not resources managed by this Terraform.

`gcp-checks.yml` runs local checks without GCP credentials. `gcp-deploy.yml` exposes initial `infra`, dev `publish`, and target `release` operations. It applies a saved plan, but its environment approval precedes that job; it does not implement a second approval of the exact generated plan. Use the manual review/apply path if that second gate is required. `gcp-flink.yml` deploys already-published Flink images using the preinstalled operator and an authorized self-hosted runner.

## Common operating procedures

### Change configuration without changing code

1. Find the setting using [the change guide](change-guide.md), then edit the intended overlay or Terraform module.
2. Validate the affected environments. A shared-default change requires checking all three.
3. Render with the **currently deployed release manifest**, save/review/apply the plan using the correct backend, and export fresh outputs. Rendering without a manifest would remove the active batch release specification and pause schedules.
4. For Flink configuration, also regenerate its manifests using the Flink release and apply the reviewed application update. Terraform apply alone does not update `job.args` in Kubernetes.
5. Run a small explicit window or stateful recovery check appropriate to the change. Record the new configuration hash and plan.

### Rotate an API secret

1. An authorized secret operator adds a new version using `gcloud secrets versions add SECRET_ID --project PROJECT_ID --data-file=SECURE_FILE_OUTSIDE_REPOSITORY`.
2. Change `secrets.ALIAS.version` to the new numeric string in the appropriate YAML. Keep the old version enabled while old jobs or rollback may still require it.
3. Render with the existing release and apply the configuration. Export outputs and run a controlled API extraction test.
4. Verify the actual Dataflow/Dataproc runtime identity can access the new version. Workers fetch secrets in Beam setup or Spark executor partitions; existing task memory is not hot-reloaded.
5. After validating new runs and completing the rollback/old-job window, the secret operator may disable the old version under the team's policy. Never place the payload in YAML, a run argument, a release manifest or Terraform.

The Flink GCS example uses Workload Identity and requires no API secret. The current secret-reader schema supports Dataflow/Dataproc only; adding a Flink external API integration requires explicit Java runtime fetching, IAM and schema changes rather than passing a plaintext key into `job.args`.

### Change schedules or retry a backfill

Batch schedules live under `jobs.JOB.schedule`. Scheduled windows are the previous UTC day, regardless of cron timezone. `enabled: false` plus Terraform apply removes the trigger; it does not stop a running job. The workflow's success is the data-job completion signal, not Scheduler's HTTP success. Monitor missing daily successes and configure notification channels; the provisioned failure alert alone has no recipients.

Preview a run with `gcp-platform run JOB --env ENV --outputs build/ENV/outputs.json --start-date YYYY-MM-DD --end-date YYYY-MM-DD --run-id UNIQUE_ID`. Add `--execute` only to submit. The end date is exclusive and the maximum window is 366 days. Resource settings and secret payloads are not permitted ad hoc arguments.

For a failed run, inspect the workflow, its underlying engine job and `control/runs/JOB/RUN_ID.json` before retrying. Claims prevent a second submission with the same retained ID. After confirming the prior job's state, retry with a new ID and select the successful output explicitly; do not delete claims blindly or combine all historical outputs. Avoid overlapping Bigtable recomputations. Cancelling only Workflows may leave the engine job running.

Flink's optional CronJob has different lifecycle semantics: it submits a bounded deployment and waits for completion. Disabling it in YAML does not delete an existing Kubernetes CronJob; explicitly suspend/delete that resource. See [the Flink scheduling procedure](flink.md) for bounded arguments, isolated outputs and cross-day matching limits.

### Roll back and maintain the platform

Reapply a previous environment release manifest to change future batch runs. This does not undo data, schema changes, IAM changes or running jobs. Flink rollback additionally needs a compatible savepoint/state schema. Never delete shared incremental checkpoint objects merely because they are old.

Review dependency upgrades through [tooling.md](tooling.md), regenerate locks, update matching runtime/plugin versions and repeat tests plus preprod smoke/recovery checks. For infrastructure retirement, stop triggers, account for active jobs, export/retain required data and state, then review an explicit destroy/migration plan. Protected databases/clusters/buckets require deliberate handling; do not disable deletion protection as part of ordinary configuration editing.

## Troubleshooting by symptom

- **Unknown YAML field or invalid type:** check `models.py` and the generated schema. Values such as worker counts must be numbers; secret version is a quoted numeric string. Fix the source YAML, not `build/*.json`.
- **Configuration hash mismatch:** source YAML and exported Terraform outputs differ. Render/apply the intended configuration with its release and export outputs again; do not manually replace the hash.
- **Missing release or paused schedule:** publish/promote a release, render with `--release`, and apply. Check whether an update accidentally rendered without the current manifest.
- **Secret permission denied:** check the engine's attached runtime account, secret-level reader grant and enabled version. Your local user successfully reading it does not prove worker access.
- **API requests time out:** check approved endpoint availability, NAT, subnet routing and the API contract. The sample intentionally rejects redirects and caps response size.
- **Docker named-pipe/daemon error:** start Docker Desktop in Linux mode and run `docker info`; publishing cannot proceed with only the CLI installed.
- **GKE connection timeout:** compare your actual public egress/VPN address with `flink.authorized_cidrs`; verify the auth plugin and runner route. Use the configured restricted access path.
- **Flink pod Pending or RocksDB disk pressure:** inspect pod events, resource requests, node pool capacity, node disk, and `rocksdb_local_disk_gb`. Increasing parallelism requires enough slots and node resources.
- **No Flink match yet:** inspect both source files, keys, business timestamps, current watermark, horizon and retention. Unmatched state expires; this is not indefinite storage.
- **Backfill duplicate claim:** inspect the original execution and engine before choosing a new run ID. A lost API response can leave a real running job.
- **Terraform replacement/delete in a sizing change:** stop and inspect changed naming, project, location and immutable properties. A new prefix or region is a migration, not necessarily an in-place resize.
- **All local checks pass but deployment fails:** inspect the real API error, IAM policy, quota and network restrictions. Mock plans neither contact Google nor compile Workflows server-side.

## Handover evidence

### Local validation recorded on 2026-09-20

- Python: 36 passed, one Spark test module skipped because PySpark was not installed locally. Beam DirectRunner tests were included.
- Java: Maven `verify` succeeded; seven Flink tests passed and the shaded JAR was produced.
- Terraform: three mocked plans passed (dev, prod, optional GKE/Bigtable); provider schema validation and formatting completed.
- Ruff: all checks passed.
- Docker image builds were not run because the local Docker Desktop Linux daemon was unavailable. GCP apply, operator installation, server-side CRD validation and cloud recovery tests were not performed.

The Python tests emitted dependency warnings about Google's upcoming minimum gRPC version. Refresh and compatibility-test the Beam/Google dependency locks before deployment; do not independently raise gRPC without checking Beam's dependency constraints.

### Deployment evidence to retain

Record the Git commit, release manifest, image digests, configuration hash, Terraform plan, state location, workflow execution/job IDs, sample output checks, secret version references, alert channel owners, and rollback procedure. For Flink, also record operator/Flink versions, JobManager endpoint access procedure, job ID, last successful checkpoint/savepoint and restore-test result.

Do not record plaintext secrets or access tokens in the runbook. The next engineer should be able to reproduce a build and identify a release without possessing production secret values.
