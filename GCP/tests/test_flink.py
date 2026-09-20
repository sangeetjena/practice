import copy
from pathlib import Path

import pytest
from pydantic import ValidationError

from jobs.flink.submitter.submit import build_run
from shared.configuration.loader import load, merge, read_yaml
from shared.configuration.models import PlatformConfig
from tooling.flink import manifests

ROOT = Path(__file__).resolve().parents[1]


def flink_config():
    return PlatformConfig.model_validate(
        merge(load(ROOT, "dev").model_dump(), read_yaml(ROOT / "config/examples/flink.yaml"))
    )


def platform():
    return {
        "repository": "asia-south1-docker.pkg.dev/test-project/data-dev",
        "buckets": {"raw": "raw-bucket", "curated": "curated-bucket"},
        "flink": {"state_bucket": "checkpoints", "service_account": "flink@test.iam.gserviceaccount.com"},
    }


def release():
    return {
        "version": "test",
        "job_image": platform()["repository"] + "/flink-join@sha256:" + "a" * 64,
        "submitter_image": platform()["repository"] + "/flink-submitter@sha256:" + "b" * 64,
    }


def test_flink_configuration_reaches_arguments_state_and_identity():
    config = flink_config()
    _, deployment, metrics, _ = manifests(config, platform(), release())
    spec = deployment["spec"]
    args = spec["job"]["args"]
    assert args[args.index("--join-horizon-seconds") + 1] == "86400"
    assert spec["flinkConfiguration"]["state.backend.type"] == "rocksdb"
    assert spec["flinkConfiguration"]["state.checkpoints.dir"].startswith("gs://checkpoints/")
    assert spec["serviceAccount"] == "flink-job"
    assert spec["flinkConfiguration"]["kubernetes.rest-service.exposed.type"] == "ClusterIP"
    assert metrics["kind"] == "PodMonitoring"


def test_bounded_schedule_uses_unique_state_and_output_and_waiting_submitter():
    config = flink_config()
    config.flink.batch_schedule.enabled = True
    _, deployment, _, resources = manifests(config, platform(), release())
    original = copy.deepcopy(deployment)
    batch = build_run(deployment, "2026-09-18", "2026-09-19")
    assert deployment == original
    assert batch["metadata"]["name"] == "join-batch-20260918"
    assert batch["spec"]["job"]["args"][-4:] == ["--start-date", "2026-09-18", "--end-date", "2026-09-19"]
    assert batch["spec"]["flinkConfiguration"]["state.checkpoints.dir"].endswith("join-batch-20260918")
    assert resources[-1]["spec"]["concurrencyPolicy"] == "Forbid"


@pytest.mark.parametrize(
    "change",
    [
        {"authorized_cidrs": []},
        {"authorized_cidrs": ["0.0.0.0/0"]},
        {"max_retention_seconds": 100},
        {"service_cidr": "10.60.0.0/20"},
    ],
)
def test_flink_rejects_unsafe_or_incoherent_configuration(change):
    values = flink_config().model_dump()
    values["flink"].update(change)
    with pytest.raises(ValidationError):
        PlatformConfig.model_validate(values)
