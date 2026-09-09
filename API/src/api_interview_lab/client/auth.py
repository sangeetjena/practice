from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Protocol


class AuthStrategy(Protocol):
    """Adds authentication information without coupling the client to one scheme."""

    def headers(self) -> dict[str, str]: ...


@dataclass(frozen=True, slots=True)
class BearerTokenAuth:
    token: str

    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}


@dataclass(frozen=True, slots=True)
class ApiKeyAuth:
    api_key: str
    header_name: str = "X-API-Key"

    def headers(self) -> dict[str, str]:
        return {self.header_name: self.api_key}


@dataclass(frozen=True, slots=True)
class BasicAuth:
    username: str
    password: str

    def headers(self) -> dict[str, str]:
        credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        return {"Authorization": f"Basic {credentials}"}
