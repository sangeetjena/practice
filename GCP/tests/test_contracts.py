import json
from pathlib import Path

import hcl2
import yaml

from shared.configuration.models import PlatformConfig

ROOT = Path(__file__).resolve().parents[1]


def test_committed_schema_matches_models():
    assert json.loads((ROOT / "config/schema/platform.schema.json").read_text()) == (
        PlatformConfig.model_json_schema()
    )


def test_all_terraform_files_parse():
    for path in (ROOT / "infrastructure").rglob("*.tf"):
        with path.open() as source:
            assert hcl2.load(source), path


def test_workflow_targets_exist_and_launches_are_not_blindly_retried():
    workflow = yaml.safe_load((ROOT / "orchestration/batch.yaml").read_text())
    steps = {key: value for step in workflow["main"]["steps"] for key, value in step.items()}
    for name, step in steps.items():
        if "next" in step:
            assert step["next"] in steps, name
        for branch in step.get("switch", []):
            if "next" in branch:
                assert branch["next"] in steps, name
    assert "retry" not in steps["launch_dataflow"]
    assert "retry" not in steps["launch_dataproc"]
    assert steps["claim_run"]["try"]["args"]["query"]["ifGenerationMatch"] == "0"
    assert "retry" in steps["get_status"]


def test_no_secret_payload_resources():
    for path in (ROOT / "infrastructure").rglob("*.tf"):
        content = path.read_text()
        assert 'resource "google_secret_manager_secret_version"' not in content
        assert 'resource "google_service_account_key"' not in content
