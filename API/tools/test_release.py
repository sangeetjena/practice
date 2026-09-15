"""Offline regression tests for deployment boundaries and generated resources."""
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
import release
from archive_builder import write_tar


def production_args():
    args = release.parser().parse_args(["deploy", "--environment", "production"])
    args.image = "ghcr.io/example/api@sha256:" + "a" * 64
    args.gateway_image = "docker.io/library/nginx@sha256:" + "b" * 64
    args.context = "production-context"
    args.namespace = "api-production"
    args.otel_endpoint = "http://otel.monitoring:4318"
    args.url = "https://api.example.com"
    args.dns = "10.96.0.10"
    return args


class ReleaseTests(unittest.TestCase):
    def test_archives_are_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory) / "a.tar", Path(directory) / "b.tar"
            write_tar(a, {"b.py": b"second", "a.py": b"first"})
            write_tar(b, {"a.py": b"first", "b.py": b"second"})
            self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_default_is_local_even_in_ci(self):
        with patch.dict(release.os.environ, {"CI": "true"}):
            self.assertEqual(release.parser().parse_args(["deploy"]).environment, "local")

    def test_production_rejects_missing_context_and_mutable_tag(self):
        for field, value in (("context", ""), ("namespace", ""),
                             ("image", "api:latest"), ("gateway_image", "nginx:latest")):
            args = production_args()
            setattr(args, field, value)
            with self.subTest(field=field), self.assertRaises(ValueError):
                release.production_manifest(args)

    def test_pull_request_cannot_deploy_production(self):
        with patch.dict(release.os.environ, {"GITHUB_EVENT_NAME": "pull_request"}):
            with self.assertRaisesRegex(ValueError, "Pull request"):
                release.production_manifest(production_args())

    def test_manifest_excludes_secrets_seed_and_database(self):
        args = production_args()
        manifest = release.production_manifest(args)
        items = manifest["items"]
        self.assertNotIn("Secret", {x["kind"] for x in items})
        self.assertNotIn("Job", {x["kind"] for x in items})
        self.assertNotIn("Namespace", {x["kind"] for x in items})
        self.assertNotIn("postgres", {x["metadata"]["name"] for x in items})
        self.assertEqual({x["metadata"]["namespace"] for x in items}, {args.namespace})
        deployments = {x["metadata"]["name"]: x for x in items if x["kind"] == "Deployment"}
        self.assertEqual(set(deployments), set(release.DEPLOYMENTS))
        for name in (*release.SERVICES, "import-worker"):
            spec = deployments[name]["spec"]
            pod = spec["template"]["spec"]
            self.assertFalse(pod["automountServiceAccountToken"])
            container = pod["containers"][0]
            self.assertEqual(container["image"], args.image)
            self.assertTrue(container["securityContext"]["readOnlyRootFilesystem"])
            if name in release.SERVICES:
                self.assertNotIn("replicas", spec)  # Do not reset the HPA on each release.
                self.assertIn("readinessProbe", container)
        self.assertTrue(all(x["spec"]["type"] == "ClusterIP"
                            for x in items if x["kind"] == "Service"))

    def test_gateway_config_changes_trigger_rollout(self):
        args = production_args()
        before = release.production_manifest(args)
        args.dns = "10.100.0.10"
        after = release.production_manifest(args)
        def annotation(value):
            return next(x for x in value["items"] if x["kind"] == "Deployment"
                        and x["metadata"]["name"] == "gateway")["spec"]["template"]["metadata"]
        self.assertNotEqual(annotation(before), annotation(after))

    def test_archive_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "bad.tar"
            with tarfile.open(bundle, "w") as archive:
                info = tarfile.TarInfo("../escape")
                info.size = 1
                archive.addfile(info, io.BytesIO(b"x"))
            with self.assertRaises(ValueError):
                release.unpack(bundle, root / "output")
            self.assertFalse((root.parent / "escape").exists())

    def test_production_preflight_failure_does_not_apply(self):
        with patch.dict(release.os.environ, {}, clear=True), patch.object(release, "kubectl") as k:
            with self.assertRaisesRegex(ValueError, "API_SMOKE_KEY"):
                release.deploy_production(production_args())
            k.assert_not_called()

    def test_failed_rollout_does_not_report_smoke_success(self):
        args = production_args()
        calls = []
        def fake_kubectl(args, *commands, **kwargs):
            calls.append(commands)
            if commands[:2] == ("get", "deployments"):
                return json.dumps({"items": []})
            if commands[:2] == ("rollout", "status"):
                raise release.subprocess.CalledProcessError(1, "kubectl")
        with tempfile.TemporaryDirectory() as directory, \
                patch.dict(release.os.environ, {"API_SMOKE_KEY": "test"}), \
                patch.object(release, "workspace", return_value=Path(directory)), \
                patch.object(release, "kubectl", side_effect=fake_kubectl), \
                patch.object(release, "smoke") as smoke:
            with self.assertRaises(release.subprocess.CalledProcessError):
                release.deploy_production(args)
            smoke.assert_not_called()
        self.assertTrue(any(c[:2] == ("apply", "--dry-run=server") for c in calls))


if __name__ == "__main__":
    unittest.main()
