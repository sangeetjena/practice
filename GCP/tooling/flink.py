"""Render and publish the optional Flink application; no cluster writes while rendering."""

import argparse
import json
from pathlib import Path

import yaml

from jobs.flink.submitter.submit import build_run
from shared.configuration.loader import fingerprint, load
from tooling.cli import (
    IMAGE,
    ROOT,
    VERSION,
    check_outputs,
    command,
    image_digest,
    read_platform,
    upload,
    write_json,
)


def release_file(path):
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if set(value) != {"version", "job_image", "submitter_image"} or not VERSION.fullmatch(value["version"]):
        raise ValueError("Invalid Flink release manifest")
    if any(not IMAGE.fullmatch(value[key]) for key in ("job_image", "submitter_image")):
        raise ValueError("Flink images must be digest-pinned Artifact Registry references")
    return value


def publish(platform, version, source=None):
    if not VERSION.fullmatch(version):
        raise ValueError("Invalid release version")
    original = release_file(source) if source else None
    if original and original["version"] != version:
        raise ValueError("Promotion preserves the original version")
    repository = platform["repository"]
    command(["gcloud", "auth", "configure-docker", repository.split("/")[0], "--quiet"])
    result = {"version": version}
    for key, name, dockerfile in [
        ("job_image", "flink-join", "jobs/flink/Dockerfile"),
        ("submitter_image", "flink-submitter", "jobs/flink/submitter/Dockerfile"),
    ]:
        tag = f"{repository}/{name}:{version}"
        if original:
            command(["gcloud", "auth", "configure-docker", original[key].split("/")[0], "--quiet"])
            command(["docker", "pull", "--platform", "linux/amd64", original[key]])
            command(["docker", "tag", original[key], tag])
        else:
            command(["docker", "build", "--platform", "linux/amd64", "-f", dockerfile, "-t", tag, "."])
        command(["docker", "push", tag])
        result[key] = image_digest(tag)
        if original and result[key].split("@")[1] != original[key].split("@")[1]:
            raise ValueError("Image digest changed during promotion")
    destination = ROOT / "build/flink" / platform["environment"] / f"{version}-release.json"
    write_json(destination, result)
    upload(str(destination), f"gs://{platform['buckets']['artifacts']}/flink-releases/{version}/release.json")
    return destination


def manifests(config, platform, release):
    f = config.flink
    if not f.enabled or not platform.get("flink"):
        raise ValueError("Enable Flink, apply Terraform, and export new outputs first")
    namespace = f.namespace
    infrastructure = platform["flink"]
    if any(
        not release[key].startswith(platform["repository"] + "/") for key in ("job_image", "submitter_image")
    ):
        raise ValueError("Promote the images into this environment's registry before rendering")
    state = "gs://" + infrastructure["state_bucket"]
    arguments = {
        "orders-uri": f"gs://{platform['buckets']['raw']}/flink/orders",
        "payments-uri": f"gs://{platform['buckets']['raw']}/flink/payments",
        "output-uri": f"gs://{platform['buckets']['curated']}/flink/orders-payments",
        "continuous": "true",
        "join-horizon-seconds": f.join_horizon_seconds,
        "allowed-lateness-seconds": f.allowed_lateness_seconds,
        "out-of-orderness-seconds": f.out_of_orderness_seconds,
        "idle-timeout-seconds": f.idle_timeout_seconds,
        "max-retention-seconds": f.max_retention_seconds,
        "window-seconds": f.window_seconds,
        "file-discovery-seconds": f.file_discovery_seconds,
        "config-hash": fingerprint(config),
    }
    deployment = {
        "apiVersion": "flink.apache.org/v1beta1",
        "kind": "FlinkDeployment",
        "metadata": {
            "name": "orders-payments",
            "namespace": namespace,
            "labels": {"platform-job": "orders-payments", "environment": config.environment},
        },
        "spec": {
            "image": release["job_image"],
            "flinkVersion": "v1_20",
            "serviceAccount": "flink-job",
            "flinkConfiguration": {
                "taskmanager.numberOfTaskSlots": str(f.task_slots),
                "state.backend.type": "rocksdb",
                "state.backend.incremental": "true",
                "state.backend.rocksdb.memory.managed": "true",
                "state.backend.rocksdb.localdir": "/opt/flink/rocksdb",
                "state.checkpoints.dir": state + "/checkpoints/orders-payments",
                "state.savepoints.dir": state + "/savepoints/orders-payments",
                "state.checkpoints.num-retained": "3",
                "execution.checkpointing.interval": f"{f.checkpoint_interval_seconds} s",
                "execution.checkpointing.timeout": f"{f.checkpoint_timeout_seconds} s",
                "execution.checkpointing.mode": "EXACTLY_ONCE",
                "execution.checkpointing.min-pause": "10 s",
                "execution.checkpointing.externalized-checkpoint-retention": "RETAIN_ON_CANCELLATION",
                "high-availability.type": "kubernetes",
                "high-availability.storageDir": state + "/ha/orders-payments",
                "kubernetes.rest-service.exposed.type": "ClusterIP",
                "kubernetes.operator.job.upgrade.last-state-fallback.enabled": "false",
                "metrics.reporters": "prom",
                "metrics.reporter.prom.factory.class": (
                    "org.apache.flink.metrics.prometheus.PrometheusReporterFactory"
                ),
                "metrics.reporter.prom.port": "9249",
                "restart-strategy.type": "fixed-delay",
                "restart-strategy.fixed-delay.attempts": "5",
                "restart-strategy.fixed-delay.delay": "10 s",
            },
            "jobManager": {
                "replicas": f.jobmanager_replicas,
                "resource": {"cpu": f.jobmanager_cpu, "memory": f.jobmanager_memory},
            },
            "taskManager": {"resource": {"cpu": f.taskmanager_cpu, "memory": f.taskmanager_memory}},
            "podTemplate": {
                "metadata": {"labels": {"platform-job": "orders-payments"}},
                "spec": {
                    "securityContext": {"fsGroup": 999},
                    "containers": [
                        {
                            "name": "flink-main-container",
                            "ports": [{"name": "metrics", "containerPort": 9249}],
                            "volumeMounts": [{"name": "rocksdb", "mountPath": "/opt/flink/rocksdb"}],
                        }
                    ],
                    "volumes": [
                        {"name": "rocksdb", "emptyDir": {"sizeLimit": f"{f.rocksdb_local_disk_gb}Gi"}}
                    ],
                },
            },
            "job": {
                "jarURI": "local:///opt/flink/usrlib/orders-payments.jar",
                "entryClass": "example.platform.JoinJob",
                "parallelism": f.parallelism,
                "upgradeMode": "savepoint",
                "state": "running",
                "args": [item for key, value in arguments.items() for item in ("--" + key, str(value))],
            },
        },
    }
    resources = [
        {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": namespace}},
        {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": "flink-job",
                "namespace": namespace,
                "annotations": {"iam.gke.io/gcp-service-account": infrastructure["service_account"]},
            },
        },
        {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {"name": "flink-runtime", "namespace": namespace},
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["pods", "services", "configmaps"],
                    "verbs": ["get", "list", "watch", "create", "update", "patch", "delete"],
                },
                {
                    "apiGroups": ["apps"],
                    "resources": ["deployments"],
                    "verbs": ["get", "list", "watch", "create", "update", "patch", "delete"],
                },
            ],
        },
        {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {"name": "flink-runtime", "namespace": namespace},
            "roleRef": {"apiGroup": "rbac.authorization.k8s.io", "kind": "Role", "name": "flink-runtime"},
            "subjects": [{"kind": "ServiceAccount", "name": "flink-job", "namespace": namespace}],
        },
    ]
    monitoring = {
        "apiVersion": "monitoring.googleapis.com/v1",
        "kind": "PodMonitoring",
        "metadata": {"name": "flink", "namespace": namespace},
        "spec": {
            "selector": {"matchLabels": {"platform-job": "orders-payments"}},
            "endpoints": [{"port": "metrics", "interval": "30s"}],
        },
    }
    schedule = []
    if f.batch_schedule.enabled:
        schedule = batch_resources(config, deployment, release)
    return resources, deployment, monitoring, schedule


def batch_resources(config, deployment, release):
    f = config.flink
    ns = f.namespace
    return [
        {"apiVersion": "v1", "kind": "ServiceAccount", "metadata": {"name": "flink-batch", "namespace": ns}},
        {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {"name": "flink-batch", "namespace": ns},
            "rules": [
                {
                    "apiGroups": ["flink.apache.org"],
                    "resources": ["flinkdeployments"],
                    "verbs": ["get", "create", "update"],
                }
            ],
        },
        {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {"name": "flink-batch", "namespace": ns},
            "roleRef": {"apiGroup": "rbac.authorization.k8s.io", "kind": "Role", "name": "flink-batch"},
            "subjects": [{"kind": "ServiceAccount", "name": "flink-batch", "namespace": ns}],
        },
        {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {"name": "flink-batch-template", "namespace": ns},
            "data": {"template.json": json.dumps(deployment)},
        },
        {
            "apiVersion": "batch/v1",
            "kind": "CronJob",
            "metadata": {"name": "flink-daily", "namespace": ns},
            "spec": {
                "schedule": f.batch_schedule.cron,
                "timeZone": f.batch_schedule.timezone,
                "concurrencyPolicy": "Forbid",
                "startingDeadlineSeconds": 600,
                "successfulJobsHistoryLimit": 2,
                "failedJobsHistoryLimit": 3,
                "jobTemplate": {
                    "spec": {
                        "backoffLimit": 1,
                        "activeDeadlineSeconds": f.batch_timeout_seconds + 120,
                        "template": {
                            "spec": {
                                "serviceAccountName": "flink-batch",
                                "restartPolicy": "Never",
                                "containers": [
                                    {
                                        "name": "submit",
                                        "image": release["submitter_image"],
                                        "resources": {
                                            "requests": {"cpu": "100m", "memory": "128Mi"},
                                            "limits": {"cpu": "500m", "memory": "256Mi"},
                                        },
                                        "env": [
                                            {"name": "NAMESPACE", "value": ns},
                                            {
                                                "name": "TIMEOUT_SECONDS",
                                                "value": str(f.batch_timeout_seconds),
                                            },
                                        ],
                                        "volumeMounts": [
                                            {"name": "config", "mountPath": "/config", "readOnly": True}
                                        ],
                                    }
                                ],
                                "volumes": [
                                    {"name": "config", "configMap": {"name": "flink-batch-template"}}
                                ],
                            }
                        },
                    }
                },
            },
        },
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["publish", "promote", "render"])
    parser.add_argument("--env", choices=["dev", "preprod", "prod"], required=True)
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument("--version")
    parser.add_argument("--release", type=Path)
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--run-id")
    args = parser.parse_args()
    config = load(ROOT, args.env)
    platform = read_platform(args.outputs)
    check_outputs(platform, config)
    if args.operation in {"publish", "promote"}:
        if not args.version or (args.operation == "promote" and not args.release):
            parser.error("Publishing needs --version; promotion also needs --release")
        print(publish(platform, args.version, args.release if args.operation == "promote" else None))
        return
    if not args.release:
        parser.error("Rendering requires --release")
    resources, deployment, monitoring, schedule = manifests(config, platform, release_file(args.release))
    target = ROOT / "build/flink" / args.env
    if args.start_date or args.end_date or args.run_id:
        if not all((args.start_date, args.end_date, args.run_id)):
            parser.error("Ad hoc rendering requires --start-date, --end-date, and --run-id")
        deployment = build_run(deployment, args.start_date, args.end_date, args.run_id)
        schedule = []
        target = target / args.run_id
    target.mkdir(parents=True, exist_ok=True)
    for name, docs in (
        ("bootstrap", resources),
        ("deployment", [deployment]),
        ("monitoring", [monitoring]),
        ("schedule", schedule),
    ):
        (target / f"{name}.yaml").write_text(yaml.safe_dump_all(docs, sort_keys=False), encoding="utf-8")
    (target / "operator-values.yaml").write_text(
        yaml.safe_dump(
            {
                "watchNamespaces": [config.flink.namespace],
                "webhook": {"create": False},
                "jobServiceAccount": {"create": False, "name": "flink-job"},
            }
        ),
        encoding="utf-8",
    )
    print(target)


if __name__ == "__main__":
    main()
