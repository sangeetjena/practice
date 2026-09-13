"""Generate local-only credentials without placing secrets in source or stdout.

Example: python scripts/bootstrap_cloud.py creates .env.cloud and local-api-key.txt.
Existing credentials are never overwritten; remove them deliberately to reset the lab.
"""

import hashlib
import json
import secrets
from pathlib import Path

root = Path(__file__).resolve().parents[1]
environment, key_file = root / ".env.cloud", root / "local-api-key.txt"
if environment.exists() or key_file.exists():
    raise SystemExit("Existing local credentials preserved. Use the existing configuration.")
key, password = secrets.token_urlsafe(32), secrets.token_hex(24)
registry = [
    {
        "sha256": hashlib.sha256(key.encode()).hexdigest(),
        "tenant_id": "acme",
        "subject": "local-owner",
        "roles": ["read", "submit", "review"],
    }
]
tenants = {
    "acme": {
        "services": ["orders"],
        "prometheus_url": "http://host.docker.internal:9090",
        "action_allowlist": [],
        "http_allowed_hosts": [],
        "github_allowed_repositories": [],
        "email_allowed_recipients": [],
    }
}
values = {
    "POSTGRES_PASSWORD": password,
    "DATABASE_URL": f"postgresql+psycopg://observer:{password}@postgres:5432/observer",
    "OBSERVE_AUTH_KEYS": json.dumps(registry),
    "OBSERVE_TENANTS": json.dumps(tenants),
    "CHROMA_HOST": "chroma",
    "CHROMA_PORT": "8000",
    "CHROMA_SSL": "false",
    "EMBEDDING_PROVIDER": "hash",
    "LLM_PROVIDER": "rule",
    "ACTION_MODE": "dry_run",
}
environment.write_text("\n".join(f"{k}='{v}'" for k, v in values.items()) + "\n")
key_file.write_text(key)
environment.chmod(0o600)
key_file.chmod(0o600)
print("Local configuration created. Read local-api-key.txt only when configuring your client.")
