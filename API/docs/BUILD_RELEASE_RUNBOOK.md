# API build, local testing, and production release runbook

## What this release path does

This is the current FastAPI orders/customers/products platform, not a Flask rewrite.
Run commands from the repository root (`practice`) unless noted otherwise.

| Command/event | Result |
|---|---|
| `bazel build //API:release` | Builds a Hatchling wheel and deterministic Docker context tar |
| `bazel test //API:deployment_tests` | Tests deployment policy and manifest generation |
| `bazel run //API:image` | Builds the bundle, then a Docker image; lint, pytest, governance and release tests must pass |
| `bazel run //API:deploy` | Builds that image, starts the isolated local stack, runs API/auth/worker smoke tests |
| Pull request | Build/test only, including existing observability and ObserveAgent checks |
| Merge to `master` | Build/test → publish tested image to GHCR → production Kubernetes rollout → read-only smoke |

Local remains the default even if `CI=true`. The production workflow explicitly selects
`--environment production`; a generic CI flag never grants production access.
No production credentials, registry account, cluster or namespace is created by these commands.

`pyproject.toml` remains the Python metadata/dependency source. Bazel uses a pinned Hatchling
tool to create the wheel inside a declared build action. Docker BuildKit installs the wheel
and runtime dependencies, tests the installed package, and creates the non-root runtime image.
The build context excludes `.env`, git history and local data. A `.pyz` is not needed for this
container deployment; no Shiv target is provided.

The wheel/context actions are Bazel-cacheable. Docker image construction is an explicit
`bazel run` action using Docker's cache, not a hermetic `rules_oci` image action. Docker and
network access are required for image builds. Python runtime dependency versions currently
resolve from `pyproject.toml` ranges; the image records the exact installed inventory in
`/build-info/requirements-resolved.txt`. Promoting its digest preserves exactly those bytes.
This does not guarantee byte-identical image rebuilds from the same source: a reviewed
transitive runtime lockfile/hash policy is still required for that stronger guarantee.

## 1. Developer prerequisites (Windows)

Install Git, Python 3.12, Docker Desktop with Linux containers, and Bazelisk (available as
`bazel`). Bazelisk reads the repository's `.bazelversion`. Native Windows Bazel also needs
its supported MSYS2 shell configuration; WSL2 with Docker Desktop integration is an alternative.
See [Bazel on Windows](https://bazel.build/install/windows) and
[Bazelisk](https://github.com/bazelbuild/bazelisk).

PowerShell:

```powershell
cd C:\path\to\practice
python --version
bazel version
docker version
docker compose version
```

Use Docker's local Desktop context, not a remote Docker host. Ensure port 8080 is free.
If the original lab is running, stop it without deleting volumes:

```powershell
docker compose --project-directory API -f API/docker-compose.yml down
```

## 2. After development: build, start, test

```powershell
# Fast offline deployment-policy checks.
bazel test //API:deployment_tests

# Full build + local deployment + live acceptance checks.
bazel run //API:deploy
```

The command builds `api-platform:local`, runs all API unit/integration tests and lint in the
build container, preserves an existing `API/.env` or generates one if missing, and starts
PostgreSQL, one local-only seed job, three APIs, the worker, and Nginx. Smoke checks validate
authenticated lists, rejection without credentials, and a completed worker import.

Local credentials and PostgreSQL data persist between starts. This isolated `api-release`
Compose project is separate from the legacy observability/ObserveAgent stack; it disables
OTel locally. The existing compatibility workflow still exercises the full telemetry stack.
To use dashboards locally, stop this stack and use the original `API/README.md` Compose flow.

Open [orders API docs](http://localhost:8080/orders/docs).

```powershell
python API/tools/release.py status
python API/tools/release.py logs --service orders
python API/tools/release.py logs --service import-worker
python API/tools/release.py smoke
```

Manual read request (credentials stay in your local shell):

```powershell
Push-Location API
$env:DEMO_API_KEY = python scripts/credentials.py --tenant acme
Pop-Location
curl.exe --fail-with-body -H "X-API-Key: $env:DEMO_API_KEY" "http://localhost:8080/orders/api/v1/orders?limit=5"
Remove-Item Env:DEMO_API_KEY
```

Build without starting services, then deploy the already-built image:

```powershell
bazel run //API:image
python API/tools/release.py deploy --skip-build
```

Choose another local port consistently:

```powershell
$env:API_PORT = "8081"
bazel run //API:deploy
python API/tools/release.py smoke
```

Stop services and keep database data:

```powershell
python API/tools/release.py stop
```

Never add `down -v` to routine stop/redeploy commands. It deletes the local database volume.
Each smoke invocation adds one uniquely keyed sample import to this local database only.

## 3. Before pushing a change

```powershell
bazel test //API:deployment_tests
bazel run //API:deploy
git diff --check
git status --short
git add <the-files-you-intend-to-change>
git commit -m "Describe the API change"
git push origin <your-feature-branch>
```

Open a pull request to `master`. Review the `API Bazel build and production release` checks.
Both the Bazel image tests and reusable compatibility checks must pass before publication.
The compatibility checks retain the original API governance, ObserveAgent and OTel smoke tests.
Configure branch protection to require these checks. Do not commit `.env`, kubeconfig,
credential JSON, local DB files or generated `API/dist` artifacts.

## 4. Production one-time prerequisites (platform/support team)

Provision the following independently of application release:

- A reachable Kubernetes cluster, explicit kubeconfig context, namespace and Metrics Server.
- PostgreSQL, schema and appropriate application DB role; backups and connection capacity.
- Secret `platform-secrets` in that namespace containing `DATABASE_URL`, `JWT_SECRET`,
  `CURSOR_SECRET`, and `CREDENTIALS_JSON`. Use real tenant credentials, not bootstrap demo users.
  `DATABASE_URL` must use `postgresql+psycopg://`; configure verified database TLS as appropriate.
- A registry pull secret if GHCR is private, and permission for the workflow to publish the package.
- A TLS ingress/load balancer routing to the generated `gateway` ClusterIP service on port 8080.
  Preserve the `/orders`, `/customers`, `/products` paths. The gateway strips the prefix.
- A reachable OTLP/HTTP collector, cluster DNS service IP and standard `cluster.local` suffix.
- Namespace-scoped deployment credentials with permission to inspect existing deployments/secrets
  and apply deployments, services, ConfigMaps, HPAs and PDBs. No cluster-admin credentials are needed.

This pipeline is provider-neutral. It accepts a kubeconfig secret; if your cloud supports OIDC,
replace that authentication step with the provider's short-lived workload identity login.
Private clusters need a runner with network access, such as a suitably isolated self-hosted runner.

### GitHub configuration

Set repository variable `API_PYTHON_BASE` to a reviewed Python 3.12 Linux image digest, for example
`docker.io/library/python@sha256:<actual-digest>`. This is required for a master-branch build.
It must match the default `linux/amd64` target; change and test the platform if your nodes use ARM.

Create a GitHub Environment named `production` and set:

| Type | Name | Value |
|---|---|---|
| Secret | `API_KUBECONFIG_B64` | Base64-encoded kubeconfig for a narrowly scoped deployment identity |
| Secret | `API_SMOKE_KEY` | A read-only API key for a real smoke-test tenant |
| Variable | `API_KUBE_CONTEXT` | Exact allowed kubeconfig context name |
| Variable | `API_NAMESPACE` | Existing application namespace, e.g. `api-production` |
| Variable | `API_KUBECTL_VERSION` | A pinned kubectl version compatible with the cluster |
| Variable | `API_URL` | HTTPS gateway origin, e.g. `https://api.example.com` |
| Variable | `API_OTEL_ENDPOINT` | Collector OTLP/HTTP base URL, without `/v1/traces` |
| Variable | `API_CLUSTER_DNS` | Cluster DNS service IP |
| Variable | `API_GATEWAY_IMAGE` | Reviewed official Nginx image by digest, compatible with UID 101 |
| Variable | `API_SECRET` | Optional; defaults to `platform-secrets` |
| Variable | `API_PULL_SECRET` | Registry pull secret name, if needed |

Never paste actual credentials into GitHub variables or workflow YAML. Restrict the production
environment to `master`; add environment review requirements if that is your release policy.
The workflow uses `GITHUB_TOKEN` for GHCR and publishes `ghcr.io/<owner>/api-platform:<commit-sha>`.

### Initial schema, without sample data

The application deployment never runs the demo seed job. For a fresh DB, set the production
environment variables above in a trusted operator shell, set `API_IMAGE` to a published digest,
and provision `platform-schema-secrets` containing an admin `DATABASE_URL` temporarily.

```powershell
python API/tools/release.py render-schema --environment production | kubectl --context $env:API_KUBE_CONTEXT -n $env:API_NAMESPACE apply -f -
kubectl --context $env:API_KUBE_CONTEXT -n $env:API_NAMESPACE wait --for=condition=complete job/api-initial-schema --timeout=180s
kubectl --context $env:API_KUBE_CONTEXT -n $env:API_NAMESPACE logs job/api-initial-schema
```

This creates missing tables with no records. A completed Job will not rerun on apply.
Restrict/remove the initialization credential after setup. Future schema changes require reviewed,
versioned migrations and expand/contract compatibility; `create_all` is not a migration system.
If first-time CI fails because the schema/ingress is not ready, finish provisioning and rerun the
failed deployment job using its already published digest.

## 5. Normal production release

Merge the tested PR to `master`. CI performs:

1. Build and test the wheel/runtime image and start it for local smoke tests.
2. Wait for the separate existing compatibility/observability checks.
3. Save/load the tested image, publish it to GHCR, and capture the immutable digest.
4. Reject a superseded release, configure the explicitly named cluster context, and validate prerequisites.
5. Save the rendered manifest and previous image references as workflow artifacts.
6. Run server-side dry-run, apply the manifest, wait for all five deployments, and test authenticated
   reads plus authentication denial against the HTTPS gateway. No production data is created.

Production never rebuilds the image, creates credentials, seeds demo data or deploys the local database.
Releases are serialized. A failed rollout or smoke check fails the workflow; it does not silently
claim success or automatically undo possibly incompatible database changes.

For a reviewed manual redeploy of an existing digest, load the same environment configuration:

```powershell
$env:API_IMAGE = "ghcr.io/<owner>/api-platform@sha256:<actual-published-digest>"
python API/tools/release.py render --environment production
python API/tools/release.py deploy --environment production
```

## 6. Support: inspect and recover

```powershell
python API/tools/release.py status --environment production
python API/tools/release.py logs --environment production --service orders
python API/tools/release.py logs --environment production --service import-worker
python API/tools/release.py smoke --environment production
kubectl --context $env:API_KUBE_CONTEXT -n $env:API_NAMESPACE get events --sort-by=.lastTimestamp
```

| Symptom | Check/action |
|---|---|
| Bazel dependency download fails | Bazel/PyPI network access, corporate certificates/proxy; retry after access is fixed |
| Build fails in `verify` stage | Read lint/pytest/governance error; fix and rebuild; do not bypass test stage |
| Local port occupied | Stop old lab or set `API_PORT` consistently |
| Local DB authentication fails | Preserve matching `.env` and DB volume; do not regenerate credentials over existing data |
| `ImagePullBackOff` | Published digest, registry access, pull secret, node architecture |
| API pods fail startup | Correct secret keys, PostgreSQL URL and credentials; production disallows SQLite/fault injection |
| Readiness fails | DB connectivity and schema; inspect pod events and API logs |
| Rollout times out | Resources/quota/scheduling, image pulls and readiness; inspect all deployments |
| HTTPS smoke fails | TLS ingress → gateway routing → ready service endpoints → API key/tenant |
| Worker has no progress | Worker logs, DB access, import job states and leases; process readiness alone is not job health |
| HPA unknown metrics | Metrics Server, resource requests and node capacity |

Restore a previous known-good application digest from the workflow's `previous-images.json`:

```powershell
$env:API_IMAGE = "ghcr.io/<owner>/api-platform@sha256:<previous-good-digest>"
python API/tools/release.py deploy --environment production
```

This keeps manifest configuration and image choice consistent. For an emergency single-deployment
rollback when configuration also needs to revert:

```powershell
python API/tools/release.py rollback --environment production --service orders
python API/tools/release.py smoke --environment production
```

`rollout undo` affects one deployment, not the shared ConfigMap or database. Reconcile the intended
version in source/release configuration afterward; the next CI deployment otherwise replaces it.
Check schema compatibility before any rollback. Never delete the namespace or DB volume to fix a rollout.

## Production readiness boundary

This change standardizes the build/release controls. It does not certify the teaching application's
authentication, shared DB model or worker design for every production workload. Complete a reviewed
runtime dependency lock/hash and vulnerability policy, versioned DB migrations, IdP-backed identity,
network policies/TLS, backup/restore tests, SLOs and load tests before exposing real customer traffic.
The production namespace, secrets, ingress and collector must exist before the first deployment.

Validation in the authoring workspace: Python syntax and offline deployment tests can run here.
Bazel, Docker and API runtime dependencies are unavailable here, so the first PR CI run must validate
the complete build, container startup and existing API tests. No production deployment was performed.
