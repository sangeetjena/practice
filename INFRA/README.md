# Local Database Platform

A database-focused, disposable kind cluster for development and platform-engineering practice. It can deploy any selection of PostgreSQL with Citus, Cassandra, Qdrant, TimescaleDB, and Redis. There is no application code, app image, or app deployment in this setup; the `workloads` namespace is reserved for clients you add later.

```text
Developer machine
  Docker + kind (1 control plane, 3 workers)
  Host-mounted data/ directories
        |
        +-- Kubernetes + Calico NetworkPolicy enforcement
              +-- PostgreSQL/Citus: coordinator + 3 workers
              +-- Cassandra: 3 nodes
              +-- Qdrant: 3 nodes
              +-- TimescaleDB: 1 node
              +-- Redis: 1 node with AOF
```

Every database replica has its own host directory under `data/`. Deleting the kind cluster does not delete those directories. This is a local learning environment, not a production HA or backup design.

## Requirements

- Docker Desktop with Linux containers, or Docker Engine
- kind, kubectl, Helm, Terraform, Make, and Bash
- Windows: WSL2 or Git Bash. Ensure Docker can share/access the directory configured by `INFRA_DATA_DIR`. In Docker Desktop, enable WSL integration for WSL2, or allow the project drive/path for Git Bash. WSL maps `C:/path` to `/mnt/c/path`; for better I/O, a directory inside the WSL Linux filesystem can be used instead.
- The full five-database profile needs substantial RAM. On a 16 GB laptop, start with TimescaleDB alone and add services as resources allow. A profile flag prevents its database pods from starting but does not reduce the size of the kind node cluster itself.

Run `make prerequisites` to check tools and that Docker is running.

## Isolated Python Environment

INFRA owns its Python environment at `INFRA/.venv`; Python dependencies are listed in `requirements-dev.txt`. From this directory in WSL, leave any other project environment and create INFRA's environment:

```bash
deactivate  # only if another virtualenv, such as GCP/.venv, is active
make setup
source .venv/bin/activate
```

Make targets and helper scripts use `.venv/bin/python` directly, so they continue using INFRA's packages even if another environment is later activated in the shell. The Dev Container runs the same `make setup` bootstrap. Infrastructure CLIs are installed separately in the Dev Container and are not Python packages.

## Configure

From this directory, create `.env` from the example and replace each placeholder with a local value:

```bash
cp .env.example .env
```

Set `ENABLE_CITUS`, `ENABLE_CASSANDRA`, `ENABLE_QDRANT`, `ENABLE_TIMESCALE`, and `ENABLE_REDIS` to `true` or `false` in `.env`. All five default to `true` for existing deployments; monitoring defaults to `false`. Only enabled services require credentials. PostgreSQL, TimescaleDB, Cassandra, Redis, and Grafana passwords must be at least 12 characters; the Qdrant API key must be at least 16. `.env`, Terraform state, rendered kind config, and database data are ignored by Git. Terraform's local state contains deployment secrets and must not be committed or shared.

For a small stock-research setup on a 16 GB laptop, start with TimescaleDB alone:

```dotenv
ENABLE_CITUS=false
ENABLE_CASSANDRA=false
ENABLE_QDRANT=false
ENABLE_TIMESCALE=true
ENABLE_REDIS=false
ENABLE_MONITORING=false
TIMESCALE_PASSWORD=your-local-password-at-least-12-characters
```

Keep `INFRA_DATA_DIR` and the port settings in the same `.env` file. `make deploy` still creates the shared kind cluster, namespaces, storage definitions, and network policies; Terraform installs only the enabled Helm releases. `make verify` checks only enabled services, and `make expose-all` forwards only enabled services. To add Redis later, set `ENABLE_REDIS=true`, set `REDIS_PASSWORD`, and run `make infra` then `make verify`.

**Changing an enabled service to `false` plans to uninstall its existing Helm release.** Run `make plan` and review the destroy actions before `make infra` or `make deploy`, which apply the plan automatically. Retained volumes and host data remain, but treat them as data requiring a backup before removal or re-enabling. The `moved.tf` declarations preserve state addresses for releases that remain enabled.

`INFRA_DATA_DIR` defaults to `./data`. It can be an absolute path; use forward slashes on Windows, for example `C:/dev/local-platform/data`. Under WSL, the script maps this to `/mnt/c/dev/local-platform/data`. The same path must be accessible to Docker Desktop.

This checkout is inside OneDrive. Before starting databases, set `INFRA_DATA_DIR` in `.env` to a directory outside OneDrive (for example `C:/local-platform-data`) so live database files are not synced or locked by a file-sync client. PV capacity values are Kubernetes claim metadata; host-path volumes do not enforce disk quotas, so monitor free disk space.

## Start

```bash
make prerequisites
make create
make plan
make infra
make status
make verify
```

`make deploy` combines `make create`, `make infra`, and `make verify` when you do not need a separate plan review. Cluster creation installs Calico (required for NetworkPolicy enforcement); `make infra` creates the namespaces and retained host-backed volumes, then applies Terraform-managed Helm releases. Terraform does not create or delete the kind cluster.

## Database Access

Run one port-forward target in a terminal and keep it open:

```bash
make expose-postgres
make expose-cassandra
make expose-qdrant
make expose-timescale
make expose-redis
make expose-all
```

Defaults are PostgreSQL/Citus `localhost:5432`, TimescaleDB `localhost:5433`, Redis `localhost:6379`, Cassandra `localhost:9042`, Qdrant REST `localhost:6333`, and Qdrant gRPC `localhost:6334`. Ports can be overridden in `.env`. All forwards bind to `127.0.0.1`; Kubernetes Services remain ClusterIP.

In-cluster names are `citus-coordinator.postgres.svc.cluster.local:5432`, `timescale.timescale.svc.cluster.local:5432`, `redis.redis.svc.cluster.local:6379`, `cassandra.cassandra.svc.cluster.local:9042`, and `qdrant.qdrant.svc.cluster.local:6333` / `:6334`. Qdrant requests require the configured API key. PostgreSQL/Citus uses database `agentdb` and TimescaleDB uses database `stock`; both use the `postgres` username. Redis requires its configured password.

## Citus Sharding

The coordinator registers three workers by Kubernetes DNS. A sample table and distribution command are in [examples/citus-sharding.sql](examples/citus-sharding.sql).

- Sharding distributes different data across workers, for example by `tenant_id`.
- Replication stores copies of data on multiple nodes for availability.
- This local setup configures three worker nodes; it does not enable automatic Citus shard replication or node failover.

Qdrant's sample collection configuration in [examples/qdrant-collection.json](examples/qdrant-collection.json) requests three shards and replication factor two. Collection creation is a database operation, not part of the infrastructure bootstrap.

## Operations

- `make stop` pauses the kind node containers without deleting the cluster; `make start` resumes them.
- `make destroy` removes Helm releases and the kind cluster. It never removes `data/`.
- `make test-network` checks the full five-database profile's service DNS, authorized client connectivity, and that an unlabeled namespace is blocked.
- `make test-persistence` requires the full five-database profile and is a destructive cluster-lifecycle test: it writes unique records, destroys/recreates the cluster, then checks records survived. It does not clean data.
- `make clean-data` permanently removes PostgreSQL, Cassandra, Qdrant, TimescaleDB, and Redis host data and requires typing `DELETE DATABASE DATA`.
- `make reset` destroys the cluster, requires typing `RESET DATABASE DATA AND CLUSTER`, removes the host data, and recreates the databases from empty directories.

Network policies deny cross-namespace access by default, allow database-internal peer traffic and DNS, and reserve access for namespaces labeled `infra.local/database-client=true`. Label a future database-client namespace only when you are ready to grant it access. Do not expose database protocols through a public Ingress.

## Scope

Prometheus and Grafana are optional through `ENABLE_MONITORING`; OpenTelemetry Collector and application workloads are not installed. The namespaces and enabled database endpoints provide a base for adding those later without coupling them to database provisioning.

# Model serving namespace

`kubernetes/namespaces/namespaces.yaml` now creates `logistic-regression`. It is labeled as a database client so its single model-serving pod can read Citus/Postgres and TimescaleDB through the existing database network policies. The ML_INFRA Helm chart owns the model Deployment and Service; INFRA owns the namespace and shared network rules. See `../ML_INFRA/README.md` for `make train`, `make deploy`, and `make predict`.
