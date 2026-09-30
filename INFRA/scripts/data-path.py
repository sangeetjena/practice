"""Prepare/validate the lab-owned data root; deletion is explicitly requested."""
import json
import os
from pathlib import Path
import shutil
import sys

root = Path(os.environ['DATA_DIR']).resolve()
infra = Path(__file__).resolve().parent.parent
marker = root / '.local-platform-data'
directories = ['postgres/coordinator', *[f'postgres/worker-{i}' for i in range(3)],
               *[f'{db}/node-{i}' for db in ('cassandra', 'qdrant') for i in range(3)]]
if root == Path(root.anchor) or root in (Path.home().resolve(), infra):
    raise SystemExit(f'Unsafe data root: {root}')
if any((root / name).is_symlink() for name in ['postgres', 'cassandra', 'qdrant', *directories]):
    raise SystemExit('Database storage directories must not be symlinks.')
mode = sys.argv[1]
if mode == 'prepare':
    for name in directories:
        (root / name).mkdir(parents=True, exist_ok=True)
    marker.write_text('local-platform-data-v1\n')
elif mode in ('validate', 'clean'):
    if not marker.is_file() or marker.read_text().strip() != 'local-platform-data-v1':
        raise SystemExit('Missing lab data marker. Run make create with the correct data path first.')
    if mode == 'clean':
        for name in ('postgres', 'cassandra', 'qdrant'):
            target = root / name
            if target.exists():
                shutil.rmtree(target)
elif mode == 'render':
    source = (infra / 'cluster/kind-config.yaml').read_text()
    print(source.replace('__DATA_HOST_PATH__', json.dumps(root.as_posix())), end='')
else:
    raise SystemExit('Expected prepare, validate, clean or render')
