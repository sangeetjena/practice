"""Get credentials only for the cluster returned by the reviewed Terraform state."""

import argparse
from pathlib import Path

from tooling.cli import command, read_platform

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs", type=Path, required=True)
    args = parser.parse_args()
    platform = read_platform(args.outputs)
    cluster = platform.get("flink")
    if not cluster:
        parser.error("Terraform output does not contain a Flink cluster")
    command(
        [
            "gcloud",
            "container",
            "clusters",
            "get-credentials",
            cluster["cluster"],
            "--region",
            cluster["region"],
            "--project",
            platform["project_id"],
        ]
    )
