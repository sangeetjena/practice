"""Pipe directly to kubectl apply -f -. DATABASE_URL must point to provisioned PostgreSQL."""
import json
import os
from pathlib import Path

values = dict(line.split('=', 1) for line in Path('.env').read_text().splitlines() if '=' in line)
url = os.environ.get('DATABASE_URL', '')
if not url.startswith('postgresql+psycopg://'):
    raise SystemExit('Set DATABASE_URL to your PostgreSQL SQLAlchemy connection URL first')
print(json.dumps({'apiVersion': 'v1', 'kind': 'Secret',
                  'metadata': {'name': 'platform-secrets', 'namespace': 'api-platform'},
                  'type': 'Opaque', 'stringData': {
                      'DATABASE_URL': url,
                      **{k: values[k].strip("'") for k in
                         ['JWT_SECRET', 'CURSOR_SECRET', 'CREDENTIALS_JSON']}}}))
