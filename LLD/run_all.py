"""Run all independent interview suites, optionally their demos, without dependencies."""

import argparse
import subprocess
import sys
from pathlib import Path

PROJECTS = ("rate-limiter", "url-router", "snake-game", "file-collections", "agent-ratings")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demos", action="store_true")
    parser.add_argument(
        "--include-tagging", action="store_true", help="also run the SQLite-backed tagging service"
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    failed = []
    projects = PROJECTS + (("tagging-service",) if args.include_tagging else ())
    for name in projects:
        directory = root / name
        print(f"Testing {name}", flush=True)
        start = "tests" if (directory / "tests").is_dir() else "."
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", start, "-v"],
            cwd=directory,
            check=False,
            timeout=90,
        )
        if result.returncode:
            failed.append(name)
            continue
        if args.demos:
            result = subprocess.run(
                [sys.executable, "demo.py"], cwd=directory, check=False, timeout=30
            )
            if result.returncode:
                failed.append(f"{name} demo")
    print("Failed: " + ", ".join(failed) if failed else f"All {len(projects)} projects passed.")
    return int(bool(failed))


if __name__ == "__main__":
    raise SystemExit(main())
