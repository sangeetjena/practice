"""Resolve X-API-Key to an immutable tenant principal using server-managed hashes.

Example registry entry: {sha256: '...', tenant_id: 'acme', subject: 'alice',
roles: ['read', 'submit', 'review']}. Credentials never enter prompts or queue messages.
"""

import hashlib
import hmac
import json
from dataclasses import dataclass

from fastapi import HTTPException


@dataclass(frozen=True)
class Principal:
    tenant_id: str
    subject: str
    roles: tuple[str, ...]

    def require(self, role):
        if role not in self.roles:
            raise HTTPException(403, "role is not permitted")


class Authenticator:
    def __init__(self, registry_json: str):
        self.entries = json.loads(registry_json)
        if not self.entries:
            raise ValueError("OBSERVE_AUTH_KEYS must contain at least one hashed credential")
        if len({entry["sha256"] for entry in self.entries}) != len(self.entries):
            raise ValueError("credential hashes must be unique")
        for entry in self.entries:
            if len(entry["sha256"]) != 64 or not entry["tenant_id"] or not entry["subject"]:
                raise ValueError("invalid credential registry")

    def authenticate(self, key: str | None) -> Principal:
        if not key:
            raise HTTPException(401, "X-API-Key is required")
        digest = hashlib.sha256(key.encode()).hexdigest()
        for entry in self.entries:
            if hmac.compare_digest(digest, entry["sha256"]):
                return Principal(entry["tenant_id"], entry["subject"], tuple(entry["roles"]))
        raise HTTPException(401, "invalid credential")
