"""Build with Hatchling from declared inputs; emit deterministic tar archives."""
import argparse
import io
import os
from pathlib import Path
import tarfile
import tempfile


def write_tar(output, files):
    with tarfile.open(output, "w", format=tarfile.PAX_FORMAT) as archive:
        for name, content in sorted(files.items()):
            info = tarfile.TarInfo(name)
            info.size = len(content)
            info.mode = 0o644
            info.mtime = 315532800
            archive.addfile(info, io.BytesIO(content))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--mode", choices=["wheel", "context"], required=True)
    parser.add_argument("--file", nargs=2, action="append", default=[])
    args = parser.parse_args()
    output = Path(args.output).resolve()
    files = {name: Path(path).read_bytes() for path, name in args.file}
    if args.mode == "wheel":
        from hatchling.build import build_wheel

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, content in files.items():
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(content)
            previous = Path.cwd()
            try:
                os.chdir(root)
                filename = build_wheel(str(root / "dist"))
                files = {"wheels/" + filename: (root / "dist" / filename).read_bytes()}
            finally:
                os.chdir(previous)
    else:
        wheel_archive = files.pop("wheel.tar")
        with tarfile.open(fileobj=io.BytesIO(wheel_archive)) as archive:
            for member in archive:
                if member.isfile():
                    files[member.name] = archive.extractfile(member).read()
    write_tar(output, files)


if __name__ == "__main__":
    main()
