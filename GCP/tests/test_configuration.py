import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from shared.configuration.loader import fingerprint, load, merge, read_yaml
from shared.configuration.models import PlatformConfig
from tooling.cli import execution_request, package, render

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("environment", ["dev", "preprod", "prod"])
def test_render_environments(environment, tmp_path):
    import shutil

    shutil.copytree(ROOT / "config", tmp_path / "config")
    config = load(tmp_path, environment)
    output = json.loads(render(tmp_path, environment).read_text())
    assert output["config"]["project_id"] == config.project_id
    assert output["config_hash"] == fingerprint(config)
    assert output["release"] is None
    assert config.jobs["clean-orders"].schedule.enabled == (environment == "prod")


def test_overrides_do_not_mutate_defaults():
    base = {"workers": {"min": 1, "max": 2}, "groups": ["a"]}
    original = copy.deepcopy(base)
    assert merge(base, {"workers": {"max": 5}, "groups": []}) == {
        "workers": {"min": 1, "max": 5},
        "groups": [],
    }
    assert base == original


@pytest.mark.parametrize(
    "update",
    [
        {"dataflow": {"max_worker": 5}},
        {"dataflow": {"initial_workers": 4, "max_workers": 2}},
        {"dataproc": {"executor_instances": 5, "max_executors": 2}},
        {"jobs": {"clean-orders": {"secret": "missing"}}},
        {"jobs": {"clean-orders": {"input_prefix": "../other/"}}},
        {"jobs": {"clean-orders": {"use_case": "daily_sales"}}},
        {"environment": "production"},
    ],
)
def test_invalid_configuration_fails_before_deployment(update):
    values = load(ROOT, "dev").model_dump()
    with pytest.raises(ValidationError):
        PlatformConfig.model_validate(merge(values, update))


def test_secret_access_and_nat_are_required():
    base = load(ROOT, "dev").model_dump()
    extra = read_yaml(ROOT / "config/examples/partner-and-bigtable.yaml")
    values = merge(base, extra)
    config = PlatformConfig.model_validate(values)
    assert config.jobs["spark-api"].secret == "partner"
    values["secrets"]["partner"]["readers"] = ["dataflow"]
    with pytest.raises(ValidationError, match="grant access"):
        PlatformConfig.model_validate(values)


def test_duplicate_yaml_keys_rejected(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("region: a\nregion: b\n")
    with pytest.raises(ValueError, match="Duplicate"):
        read_yaml(path)


def test_backfill_arguments_are_separate_from_infrastructure():
    platform = {
        "project_id": "project-dev",
        "region": "asia-south1",
        "workflows": {"clean-orders": "data-dev-clean-orders"},
    }
    url, body = execution_request(platform, "clean-orders", "2026-09-01", "2026-09-20", "bf-sept-v1")
    assert url.endswith("/workflows/data-dev-clean-orders/executions")
    assert json.loads(body["argument"]) == {
        "start_date": "2026-09-01",
        "end_date": "2026-09-20",
        "run_id": "bf-sept-v1",
    }
    with pytest.raises(ValueError):
        execution_request(platform, "unknown", "2026-09-01", "2026-09-20", "bf-sept-v1")
    with pytest.raises(ValueError):
        execution_request(platform, "clean-orders", "2026-09-01", "2026-09-20", "../../escape")


def test_archive_contains_shared_runtime_and_is_reproducible(tmp_path):
    import hashlib
    import shutil
    import zipfile

    for directory in ("jobs", "shared"):
        shutil.copytree(ROOT / directory, tmp_path / directory)
    archive = package(tmp_path, "test") / "platform.zip"
    first = hashlib.sha256(archive.read_bytes()).hexdigest()
    package(tmp_path, "test")
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == first
    with zipfile.ZipFile(archive) as zipped:
        assert "shared/authentication/secrets.py" in zipped.namelist()
        assert not any("credentials" in path for path in zipped.namelist())
