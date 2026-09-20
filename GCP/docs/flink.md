# Flink implementation and operating runbook

The optional example joins order and payment events from two independently monitored GCS sources. Terraform provisions GKE and cloud identities; the Flink Kubernetes Operator manages the application. Maven builds the Java job, Docker packages it, and Python renders Kubernetes YAML from the same environment configuration used by Terraform.

## 1. Configure and provision

Follow [the setup runbook](setup-runbook.md) through infrastructure deployment. Merge the `flink` and networking settings from `config/examples/flink.yaml` into your environment overlay. Replace the example authorized network with your administrator/CI egress CIDR. Enable NAT for private nodes. Run bootstrap with `enable_flink=true` to grant the infrastructure deployer the required GKE role. Re-render, plan, and apply the environment root, then export fresh Terraform outputs.

Terraform creates a regional Standard GKE cluster with private nodes, restricted public control-plane access, separate pod/service address ranges, autoscaling node pool, Workload Identity, and managed logging/Prometheus. The node service account can pull Artifact Registry images. The `flink-job` Kubernetes service account impersonates a separate runtime Google service account with input-read, output-write, and checkpoint-bucket permissions. No service-account key file is shipped in the image.

The versioned checkpoint bucket has no automatic age-based deletion: incremental RocksDB checkpoints can share older SST objects. Deleting those objects by age can corrupt a newer checkpoint. Production resource deletion protection is configured through the environment.

Dev, preprod, and prod use distinct projects, state, buckets, images and identities. Configure node sizes, parallelism, slots, JobManager/TaskManager memory and CPU, local RocksDB disk, join timing, and checkpoint timing under `flink` in YAML. Kubernetes manifests use actual Terraform output names and reject a configuration hash mismatch.

## 2. Build and publish

The compatibility baseline is Java 17, Flink 1.20.3, Maven 3.9.9 and Kubernetes Operator 1.12.0. These are deliberate pins, not claims about the newest releases. Upgrade the job, runtime image, plugins and operator together after recovery testing.

From `GCP`, with Java/Maven, Docker and gcloud installed:

```powershell
mvn -B -f jobs/flink/pom.xml verify
python -m tooling.flink publish --env dev --outputs build/dev/outputs.json --version v1.0.0
python -m tooling.flink render --env dev --outputs build/dev/outputs.json --release build/flink/dev/v1.0.0-release.json
```

The Docker build runs tests and packages the shaded application JAR. Flink runtime libraries remain provided dependencies. The image installs matching GCS filesystem and Prometheus plugins. A separate small Python image submits bounded scheduled runs. Release manifests contain immutable image digests. Use `tooling.flink promote` with `--env`, target `--outputs`, original `--release`, and the same `--version` to copy images without rebuilding.

## 3. Install the operator and deploy

Run from an address allowed by the cluster's authorized networks. Install kubectl, the GKE authentication plugin, gcloud and Helm first.

```powershell
$env:KUBECONFIG = Join-Path (Get-Location) 'build/flink-dev-kubeconfig'
python -m tooling.connect_gke --outputs build/dev/outputs.json
kubectl apply -f build/flink/dev/bootstrap.yaml
helm repo add flink-operator https://archive.apache.org/dist/flink/flink-kubernetes-operator-1.12.0/
helm repo update
helm upgrade --install flink-operator flink-operator/flink-kubernetes-operator --version 1.12.0 --namespace flink-operator --create-namespace --values build/flink/dev/operator-values.yaml --wait
kubectl apply --dry-run=server -f build/flink/dev/deployment.yaml
kubectl apply -f build/flink/dev/monitoring.yaml
kubectl apply -f build/flink/dev/deployment.yaml
kubectl get flinkdeployments -n flink
kubectl get pods -n flink
```

The generated operator values disable the admission webhook to avoid an implicit cert-manager dependency. Server-side dry-run validates the CRD schema; it does not replace runtime validation. The repository's `gcp-flink.yml` deployment workflow expects the operator already installed and a self-hosted runner labeled `gcp-deploy` with network access. Treat operators and cluster deployers as privileged administrators. Grant additional human access through reviewed GKE IAM and namespace RBAC; the runtime role is not a human editor role.

The continuously running application uses its own JobManager and TaskManagers, not a shared session cluster. The operator reconciles failures and savepoint upgrades. Kubernetes places pods; the operator submits the JAR and YAML `job.args` to Flink.

## 4. Supply the two streams

Upload immutable JSONL objects below `gs://RAW_BUCKET/flink/orders/event_date=YYYY-MM-DD/` and `gs://RAW_BUCKET/flink/payments/event_date=YYYY-MM-DD/`. See `jobs/flink/fixtures`. Each event has `event_id`, `order_id`, ISO-8601 `event_time`, and nonnegative integer `amount_cents`. Do not append to or overwrite discovered objects. Each source independently discovers new files.

This example assumes one order and one payment per globally unique order ID. Identical replayed events are suppressed while state is retained; conflicting versions are rejected. Partial payments and multiple payments require a different state model. File-source discovery state grows with processed files; use a separately implemented Kafka source for high-volume long-lived log ingestion.

Both streams are keyed by `order_id`. Managed state retains whichever event arrives first. A matching counterpart produces `SETTLED` or `AMOUNT_MISMATCH`; a tombstone suppresses duplicates until cleanup. The default join horizon is 24 hours, allowed lateness one hour, out-of-orderness 30 seconds, idle-source timeout two minutes, and maximum processing-time retention three days.

Watermarks follow the minimum of active input watermarks. Idleness prevents an inactive input from blocking progress forever. Event-time timers expire unmatched keys after the horizon plus allowed lateness; a processing-time timer bounds state even when watermarks stop. Consequently this is bounded waiting, not a promise to retain keys indefinitely. Expired, conflicting, and out-of-interval records go to the rejected output with reasons. A counterpart outside the retention contract requires reconciliation/backfill.

Joined records carry the later business timestamp while preserving upstream watermarks. Five-minute status windows emit cumulative `window_upsert` records with window start and status as their logical key. Allowed-late arrivals update the total; downstream consumers must upsert, not sum every emitted cumulative version. Matches too late for the aggregate still appear in joined output and also in the `window-late` output with reason `WINDOW_ALREADY_CLOSED`.

## 5. Checkpoints and recovery

RocksDB uses writable local `emptyDir` storage, with pod filesystem group 999. Local storage is disposable; durable incremental checkpoints, savepoints and Kubernetes HA metadata live in GCS. Checkpoint interval, timeout and retention are generated from YAML. Exactly-once checkpoint mode coordinates source position, managed join state and file sinks. It does not guarantee end-to-end deduplication across independently launched backfills and streaming jobs.

Stable operator UIDs support recovery. Upgrades use savepoints and disable automatic last-state fallback. Before changing key serializers, state schemas or operator topology, test restoration from a representative savepoint. Keep referenced images and checkpoint files available. Do not manually remove SST objects from a live checkpoint tree.

## 6. JobManager endpoint

The internal REST/UI endpoint is `http://orders-payments-rest.flink.svc.cluster.local:8081` for the default namespace. This is Flink's JobManager, rather than Hadoop's JobTracker. It is a ClusterIP service with no public ingress. Authorized operators can use:

```powershell
kubectl port-forward -n flink service/orders-payments-rest 8081:8081
```

Open `http://localhost:8081`. REST routes include `/overview`, `/jobs/overview`, `/jobs/JOB_ID/checkpoints`, and `/jobs/JOB_ID/exceptions`. Bounded runs have their own deployment-name-based REST service. Obtain actual namespace and resource details from generated manifests and Terraform outputs.

## 7. Scheduling, ad hoc runs and backfills

For an optional daily bounded job, enable `flink.batch_schedule` in YAML, regenerate manifests, and apply `schedule.yaml`. The Kubernetes CronJob starts the submitter, which creates a distinct bounded FlinkDeployment for the previous UTC date. The schedule timezone controls the trigger, while data dates remain UTC. It waits for FINISHED, reports failure, and requests suspension on timeout. `concurrencyPolicy: Forbid` prevents overlapping submitter jobs; inspect orphaned deployments if a submitter is killed. Existing runs are checked for matching arguments and image before reuse. Missed days are not automatically backfilled.

Disabling a schedule in YAML does not delete an already existing Kubernetes CronJob. Explicitly suspend it with `kubectl patch cronjob flink-daily -n flink --type merge -p '{"spec":{"suspend":true}}'`, or delete that CronJob through your deployment process. Review and remove completed bounded FlinkDeployment resources after retaining required results and diagnostics.

For an explicit backfill:

```powershell
python -m tooling.flink render --env dev --outputs build/dev/outputs.json --release build/flink/dev/v1.0.0-release.json --start-date 2026-09-18 --end-date 2026-09-19 --run-id bf-sept18-v1
kubectl apply --dry-run=server -f build/flink/dev/bf-sept18-v1/deployment.yaml
kubectl apply -f build/flink/dev/bf-sept18-v1/deployment.yaml
```

Dates are start-inclusive/end-exclusive, limited to 366 days. Rendering passes them as external job arguments, selects bounded source partitions, and isolates run output and state paths. Include both event dates when matching across midnight. Running only one day's partitions cannot find a counterpart stored the next day. Reconcile overlapping streaming and backfill outputs before publishing a canonical dataset.

## 8. Metrics, logs and acceptance checks

Flink's Prometheus reporter exposes port 9249. Generated `PodMonitoring` selects the labeled JobManager and TaskManager pods for GKE Managed Service for Prometheus. Native metrics cover checkpoints, throughput, backpressure, JVM memory and task failures. Custom join metrics count matches, duplicates, accepted/rejected late events, unmatched expirations and conflicts, with last-watermark/lag gauges. Counters reset on task restart: use rates/increases. Do not introduce order IDs as metric labels.

JSON console logs go to GKE Cloud Logging; startup logs include the configuration fingerprint and mode. This implementation provides metrics and logs, not distributed OpenTelemetry tracing. Configure Cloud Monitoring notification channels and alerts for checkpoint failures/stalls, repeated restarts, increasing unmatched events and sustained backpressure. Inspect exported metric names before writing queries; job/task scopes affect their names.

Local Maven tests cover both arrival orders, duplicate suppression, expiry, late rejection, processing-time cleanup, mismatches, state snapshot/restore and timestamp/watermark propagation. They do not prove cloud IAM, GCS checkpoint recovery, operator compatibility or RocksDB recovery on GKE. Before production: run fixture data, observe two matches and one unmatched expiry in bounded mode, verify checkpoints, restart a TaskManager, verify recovery without duplicate committed output, and exercise savepoint upgrades and late arrivals. Build both Docker images and perform the server-side CRD validation in your target cluster.

## References

- [Flink state backends](https://nightlies.apache.org/flink/flink-docs-release-1.20/docs/ops/state/state_backends/)
- [Flink GCS filesystem](https://nightlies.apache.org/flink/flink-docs-release-1.20/docs/deployment/filesystems/gcs/)
- [Operator job management](https://nightlies.apache.org/flink/flink-kubernetes-operator-docs-release-1.12/docs/custom-resource/job-management/)
- [GCP Flink monitoring](https://docs.cloud.google.com/stackdriver/docs/managed-prometheus/exporters/flink)
- [GKE Workload Identity](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/workload-identity)
