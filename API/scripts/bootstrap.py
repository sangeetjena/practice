"""Generate local-only secrets. Writes ignored .env, never prints credentials."""
import json
import secrets
from pathlib import Path

path = Path('.env')
if path.exists():
    raise SystemExit('.env exists; preserve your existing credentials')
users = {tenant: {'tenant': tenant, 'password': secrets.token_urlsafe(24),
                  'api_key': secrets.token_urlsafe(32), 'scopes': ['read', 'write']}
         for tenant in ('acme', 'globex')}
content = '\n'.join([
    'JWT_SECRET=' + secrets.token_urlsafe(48),
    'CURSOR_SECRET=' + secrets.token_urlsafe(48),
    'POSTGRES_PASSWORD=' + secrets.token_urlsafe(32),
    "CREDENTIALS_JSON='" + json.dumps(users, separators=(',', ':')) + "'",
]) + '\n'
path.write_text(content)
path.chmod(0o600)
print('Created .env. Keep it local; Compose reads it automatically.')
