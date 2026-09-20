"""Cross-platform entry point. Cloud writes require an explicit command or --execute."""

import argparse
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from shared.configuration.loader import fingerprint, load
from shared.configuration.models import PlatformConfig
from shared.runtime import validate_window

ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENTS = ["dev", "preprod", "prod"]
RUN_ID = re.compile(r"^[a-z][a-z0-9-]{2,23}$")
VERSION = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$")
IMAGE = re.compile(r"^[a-z0-9-]+-docker\.pkg\.dev/[a-z0-9-]+/[a-z0-9-]+/[a-z0-9-]+@sha256:[a-f0-9]{64}$")


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_platform(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    # Accept either `terraform output -json` or `terraform output -json platform`.
    if "platform" in data:
        data = data["platform"]["value"]
    for field in ("project_id", "region", "environment", "config_hash", "buckets", "repository", "workflows"):
        if field not in data:
            raise ValueError(f"Terraform output is missing {field}")
    return data


def read_release(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    required = {
        "version",
        "dataflow_image",
        "launcher_image",
        "dataproc_image",
        "dataflow_template_uri",
        "dataproc_main_uri",
        "python_archive_uri",
    }
    if set(data) != required:
        raise ValueError(f"Release manifest must have exactly these fields: {sorted(required)}")
    if not VERSION.fullmatch(data["version"]):
        raise ValueError("Invalid release version")
    for key in ("dataflow_image", "launcher_image", "dataproc_image"):
        if not IMAGE.fullmatch(data[key]):
            raise ValueError(f"{key} must be an Artifact Registry sha256 image reference")
    for key in ("dataflow_template_uri", "dataproc_main_uri", "python_archive_uri"):
        if not re.fullmatch(r"gs://[a-z0-9.-]+/releases/[a-zA-Z0-9._/-]+", data[key]):
            raise ValueError(f"Invalid release URI: {key}")
        if ".." in data[key]:
            raise ValueError("Traversal is not permitted in release paths")
    return data


def check_outputs(platform, config):
    if platform["project_id"] != config.project_id or platform["environment"] != config.environment:
        raise ValueError("Terraform output belongs to a different project or environment")
    if platform["config_hash"] != fingerprint(config):
        raise ValueError("Configuration changed since Terraform apply; apply the reviewed change first")


def render(root: Path, environment: str, release_path: Path | None = None) -> Path:
    config = load(root, environment)
    release = read_release(release_path) if release_path else None
    if release:
        expected_bucket = f"gs://{config.project_id}-{config.name}-{environment}-artifacts/releases/"
        expected_repo = f"{config.region}-docker.pkg.dev/{config.project_id}/{config.name}-{environment}/"
        if any(
            not release[key].startswith(expected_bucket)
            for key in ("dataflow_template_uri", "dataproc_main_uri", "python_archive_uri")
        ) or any(
            not release[key].startswith(expected_repo)
            for key in ("dataflow_image", "launcher_image", "dataproc_image")
        ):
            raise ValueError("Promote the release into this environment's registry and bucket first")
    target = root / "build" / environment / "platform.tfvars.json"
    write_json(
        target, {"config": config.model_dump(), "config_hash": fingerprint(config), "release": release}
    )
    return target


def package(root: Path, version: str) -> Path:
    if not VERSION.fullmatch(version):
        raise ValueError("Use a release version containing letters, numbers, dots, hyphens or underscores")
    target = root / "build" / "releases" / version
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target / "platform.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for directory in ("shared", "jobs"):
            for source in sorted((root / directory).rglob("*.py")):
                # Fixed timestamps make identical sources produce an identical archive.
                entry = zipfile.ZipInfo(source.relative_to(root).as_posix(), date_time=(2020, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(entry, source.read_bytes())
    shutil.copyfile(root / "jobs/dataproc/main.py", target / "spark_main.py")
    return target


def command(argv, *, cwd=ROOT, capture=False):
    executable = shutil.which(argv[0])
    if executable is None:
        raise ValueError(f"Install {argv[0]} and put it on PATH")
    result = subprocess.run([executable, *argv[1:]], cwd=cwd, check=True, text=True, capture_output=capture)
    return result.stdout.strip() if capture else None


def image_digest(tag: str) -> str:
    digest = command(
        ["gcloud", "artifacts", "docker", "images", "describe", tag, "--format=value(image_summary.digest)"],
        capture=True,
    )
    if not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
        raise ValueError("Registry did not return a valid image digest")
    return tag.rsplit(":", 1)[0] + "@" + digest


def upload(source: str, destination: str):
    # A release path cannot silently overwrite a previously published artifact.
    command(["gcloud", "storage", "cp", source, destination, "--if-generation-match=0"])


def publish(root: Path, platform: dict, version: str, source_release: Path | None = None) -> Path:
    if not VERSION.fullmatch(version):
        raise ValueError("Invalid release version")
    source = read_release(source_release) if source_release else None
    if source and source["version"] != version:
        raise ValueError("Promotion must preserve the release version")
    target = package(root, version) if source is None else root / "build/releases" / version
    target.mkdir(parents=True, exist_ok=True)
    registry = platform["repository"]
    command(["gcloud", "auth", "configure-docker", registry.split("/")[0], "--quiet"])
    images = {}
    for key, image_name, dockerfile, stage in [
        ("dataflow_image", "beam-worker", "jobs/dataflow/Dockerfile", "worker"),
        ("launcher_image", "beam-launcher", "jobs/dataflow/Dockerfile", "launcher"),
        ("dataproc_image", "spark", "jobs/dataproc/Dockerfile", None),
    ]:
        tag = f"{registry}/{image_name}:{version}"
        if source:
            source_host = source[key].split("/")[0]
            command(["gcloud", "auth", "configure-docker", source_host, "--quiet"])
            command(["docker", "pull", "--platform", "linux/amd64", source[key]])
            command(["docker", "tag", source[key], tag])
        else:
            args = ["docker", "build", "--platform", "linux/amd64", "-f", dockerfile, "-t", tag]
            if stage:
                args += ["--target", stage]
            command([*args, "."], cwd=root)
        command(["docker", "push", tag])
        images[key] = image_digest(tag)
        if source and images[key].split("@")[1] != source[key].split("@")[1]:
            raise ValueError("Promotion changed an image digest; stop and investigate")
    prefix = f"gs://{platform['buckets']['artifacts']}/releases/{version}"
    if source:
        upload(source["dataproc_main_uri"], f"{prefix}/spark_main.py")
        upload(source["python_archive_uri"], f"{prefix}/platform.zip")
        # Preserve the source release's template metadata as well as its executable images.
        command(["gcloud", "storage", "cp", source["dataflow_template_uri"], str(target / "flex.json")])
        template = json.loads((target / "flex.json").read_text(encoding="utf-8"))
        template["image"] = images["launcher_image"]
    else:
        upload(str(target / "spark_main.py"), f"{prefix}/spark_main.py")
        upload(str(target / "platform.zip"), f"{prefix}/platform.zip")
        template = {
            "image": images["launcher_image"],
            "sdkInfo": {"language": "PYTHON"},
            "metadata": json.loads((root / "jobs/dataflow/metadata.json").read_text(encoding="utf-8")),
        }
    write_json(target / "flex.json", template)
    upload(str(target / "flex.json"), f"{prefix}/flex.json")
    release = {
        "version": version,
        **images,
        "dataflow_template_uri": f"{prefix}/flex.json",
        "dataproc_main_uri": f"{prefix}/spark_main.py",
        "python_archive_uri": f"{prefix}/platform.zip",
    }
    manifest = target / f"{platform['environment']}-release.json"
    write_json(manifest, release)
    upload(str(manifest), f"{prefix}/release.json")
    return manifest


def execution_request(
    platform: dict, job: str, start_date: str, end_date: str, run_id: str
) -> tuple[str, dict]:
    validate_window(start_date, end_date)
    if not RUN_ID.fullmatch(run_id):
        raise ValueError("run_id must be 3-24 lowercase letters/digits/hyphens, starting with a letter")
    if job not in platform["workflows"]:
        raise ValueError(f"Unknown job: {job}")
    workflow = platform["workflows"][job]
    url = (
        f"https://workflowexecutions.googleapis.com/v1/projects/{platform['project_id']}"
        f"/locations/{platform['region']}/workflows/{workflow}/executions"
    )
    return url, {"argument": json.dumps({"start_date": start_date, "end_date": end_date, "run_id": run_id})}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "render"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--env", choices=ENVIRONMENTS, required=True)
        if name == "render":
            cmd.add_argument("--release", type=Path)
    sub.add_parser("schema")
    cmd = sub.add_parser("package")
    cmd.add_argument("--version", required=True)
    for name in ("publish", "promote"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--env", choices=ENVIRONMENTS, required=True)
        cmd.add_argument("--outputs", type=Path, required=True)
        cmd.add_argument("--version", required=True)
        if name == "promote":
            cmd.add_argument("--source-release", type=Path, required=True)
    cmd = sub.add_parser("run")
    cmd.add_argument("job")
    cmd.add_argument("--env", choices=ENVIRONMENTS, required=True)
    cmd.add_argument("--outputs", type=Path, required=True)
    cmd.add_argument("--start-date", required=True)
    cmd.add_argument("--end-date", required=True)
    cmd.add_argument("--run-id", required=True)
    cmd.add_argument("--execute", action="store_true", help="Submit; otherwise print the request only")
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            config = load(ROOT, args.env)
            print(f"{args.env}: valid; sha256={fingerprint(config)}")
        elif args.command == "schema":
            path = ROOT / "config/schema/platform.schema.json"
            write_json(path, PlatformConfig.model_json_schema())
            print(path)
        elif args.command == "render":
            print(render(ROOT, args.env, args.release))
        elif args.command == "package":
            print(package(ROOT, args.version))
        else:
            config = load(ROOT, args.env)
            platform = read_platform(args.outputs)
            check_outputs(platform, config)
            if args.command in {"publish", "promote"}:
                if "replace-me" in config.project_id:
                    raise ValueError("Replace example project IDs before publishing")
                print(publish(ROOT, platform, args.version, getattr(args, "source_release", None)))
            else:
                url, body = execution_request(platform, args.job, args.start_date, args.end_date, args.run_id)
                if not args.execute:
                    print(json.dumps({"url": url, "body": body}, indent=2))
                else:
                    import google.auth
                    from google.auth.transport.requests import AuthorizedSession

                    credentials, _ = google.auth.default(
                        scopes=["https://www.googleapis.com/auth/cloud-platform"]
                    )
                    response = AuthorizedSession(credentials).post(url, json=body, timeout=60)
                    response.raise_for_status()
                    print(json.dumps(response.json(), indent=2))
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
