# Server, Kubernetes, scaling and load balancing

## 1. Single server

Start with README's Compose flow. It runs three separately deployable processes but deliberately
shares one PostgreSQL database for a compact lab. Tables have tenant/kind keys; this is application
isolation, not database-role isolation. A production service split would give each service its own
schema/database role and migrations. Do not share SQLite files across pods.

VM public traffic: DNS → managed TLS load balancer → private VM:8080 → Nginx → service replicas.
Keep Compose's localhost binding when a same-host TLS proxy is used. If an external private load
balancer must reach the VM, bind the gateway to the VM's private address and restrict the firewall
to that load balancer. Configure health checks, trusted proxy handling, certificate renewal and
access controls before exposure. Never expose PostgreSQL, Jaeger, or Prometheus directly.

Nginx distributes new upstream connections across resolved addresses; persistent HTTP/2 or
keepalive connections can make request distribution uneven. It cannot create service replicas.
Compose `--scale` creates replicas; Kubernetes HPA automates replica changes. Neither adds physical
node capacity by itself.

## 2. Kubernetes prerequisites

You need a working cluster/kubectl context, registry access, Metrics Server for HPA, and PostgreSQL
reachable from the namespace. The supplied LoadBalancer Service requires a cloud LB implementation
or a local equivalent such as MetalLB. On kind/minikube use port-forward for the lab.

Manifests assume the standard `cluster.local` DNS suffix and `kube-dns` Service. Adapt the gateway
resolver/upstream suffix if the cluster uses different DNS settings. Observability pods are a
small ephemeral teaching deployment, not an HA monitoring installation.

## 3. Build and configure

Run from API. Use the tested image tag consistently in both apps.yaml and seed.yaml.

```bash
docker build -f Dockerfile.platform -t YOUR_REGISTRY/api-platform:0.3.0 .
docker push YOUR_REGISTRY/api-platform:0.3.0
kubectl create namespace api-platform
# Set DATABASE_URL securely, e.g. postgresql+psycopg://USER:PASSWORD@HOST/DATABASE?sslmode=require
# PowerShell: $env:DATABASE_URL = '...'; Bash: export DATABASE_URL='...'
python scripts/k8s_secret.py | kubectl apply -f -
```

Replace every `image: api-platform:local` in `deploy/platform/k8s/apps.yaml` and `seed.yaml` with
your registry tag (or load the image into a local kind cluster). These are explicit placeholders,
not a claim that an image has been published. Private registries may need imagePullSecrets.
The seed command creates tables and sample data. Future schema changes need versioned migrations.

## 4. Initialize once, then deploy replicas

```bash
kubectl apply -f deploy/platform/k8s/seed.yaml
kubectl -n api-platform wait --for=condition=complete job/platform-seed --timeout=120s
kubectl apply -f deploy/platform/k8s/observability.yaml
kubectl apply -f deploy/platform/k8s/apps.yaml
kubectl -n api-platform rollout status deployment/orders
kubectl -n api-platform rollout status deployment/customers
kubectl -n api-platform rollout status deployment/products
kubectl -n api-platform port-forward service/gateway 8080:8080
```

A seed job failure must be resolved before traffic is enabled. Do not run seeding from every
application pod. Reusing a completed Job does not rerun it; for another seed execution delete
only the old completed `platform-seed` job and reapply it. Do not delete application data.

The app deployments include startup/readiness/liveness probes, non-root execution, dropped
capabilities, resource requests/limits, two replicas, a rolling-update policy, HPA and PDB.
Readiness checks schema/database availability; liveness checks the process. Graceful Uvicorn
shutdown closes clients and flushes spans and metrics within the pod termination grace period.

## 5. Traffic path and scaling

Cloud LB → `gateway` Service port 8080 → Nginx pods → `orders` ClusterIP:8000 → ready orders pods.
The cloud LB is L4 here. Nginx supplies L7 path routing. ClusterIP/EndpointSlices provide stable
service discovery and transport-level distribution; the gateway resolves Service DNS, not pod
names. For large deployments use a managed Gateway API/Ingress controller with TLS instead of
maintaining a bespoke gateway. The sample itself is HTTP: terminate TLS before public traffic.

```bash
kubectl -n api-platform get hpa
kubectl -n api-platform top pods
kubectl -n api-platform get endpointslices
kubectl -n api-platform describe hpa orders
```

HPA targets 65% CPU, min 2/max 6 pods. CPU is a simple lab signal; I/O-bound APIs may need request
concurrency, latency or queue-depth scaling through a metrics adapter. A PDB constrains voluntary
eviction, not node failure. HPA does not scale PostgreSQL; budget DB connections as
`max pods × per-pod pool size`, leaving headroom for migrations/admin. Pool timeouts should fail
within upstream deadlines rather than accumulate unbounded requests.

## 6. Observability and diagnosis

```bash
kubectl -n api-platform port-forward service/prometheus 9090:9090
kubectl -n api-platform port-forward service/jaeger 16686:16686
kubectl -n api-platform logs deployment/orders --tail=50
kubectl -n api-platform get pods,services,endpointslices
kubectl -n api-platform describe pod POD_NAME
```

Applications push OTLP metrics and traces to the Collector Service. The Collector routes traces to
Jaeger and exposes Prometheus-format metrics on port 8889; Prometheus scrapes that single endpoint.
Metric resource/point attributes preserve the originating service across replicas. This is simpler
than exposing per-process endpoints, but the Collector needs its own availability, capacity and
backpressure plan. Grafana is provisioned in Compose; use an existing cluster Grafana with the same
dashboard and Prometheus datasource, or port-forward Prometheus/Jaeger for this Kubernetes lab.

Failure sequence: check gateway status → service endpoints → readiness → DB connectivity →
application error/latency metrics → trace child span → correlated log. A heartbeat/process probe
alone cannot prove the endpoint is working correctly.

## 7. Before production

Add managed TLS, network policies, external secrets, asymmetric identity verification, database
roles/RLS, schema migrations, backup/restore drills, durable monitoring storage, Alertmanager
routes, distributed tenant quotas, dependency/image scanning, topology spreading, node autoscaling,
and load tests. Choose an actual SLO and measure it before changing capacity settings.
