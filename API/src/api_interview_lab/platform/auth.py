"""Authentication establishes identity; every endpoint separately enforces scope."""
import secrets
from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import APIKeyHeader, HTTPBasic, HTTPBasicCredentials, HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

api_key = APIKeyHeader(name="X-API-Key", auto_error=False)
basic = HTTPBasic(auto_error=False)
bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Principal:
    tenant: str
    subject: str
    scopes: frozenset[str]


def authenticate(
    request: Request,
    key: Annotated[str | None, Depends(api_key)],
    basic_value: Annotated[HTTPBasicCredentials | None, Depends(basic)],
    token: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> Principal:
    cfg = request.app.state.settings
    # Ambiguous credentials must not silently select the more privileged identity.
    if sum(x is not None for x in (key, basic_value, token)) != 1:
        raise HTTPException(401, "Provide exactly one supported credential")
    record = None
    if token:
        try:
            record = jwt.decode(token.credentials, cfg.jwt_secret, algorithms=["HS256"],
                                issuer=cfg.issuer, audience=cfg.audience,
                                options={"require": ["exp", "iat", "sub", "tenant", "scopes"]})
        except jwt.PyJWTError:
            raise HTTPException(401, "Invalid or expired token") from None
    else:
        for subject, candidate in cfg.credentials.items():
            match = (key is not None and bool(candidate.get("api_key")) and
                     secrets.compare_digest(key, candidate["api_key"]))
            if basic_value:
                match = (secrets.compare_digest(basic_value.username, subject) and
                         secrets.compare_digest(basic_value.password, candidate.get("password", "")))
            if match:
                record = {**candidate, "sub": subject}
                break
    if (not record or not isinstance(record.get("tenant"), str) or not record["tenant"]
            or not isinstance(record.get("sub"), str)
            or not isinstance(record.get("scopes"), list)
            or not all(isinstance(s, str) for s in record["scopes"])):
        raise HTTPException(401, "Invalid credential identity")
    principal = Principal(record["tenant"], record["sub"], frozenset(record["scopes"]))
    request.state.principal = principal
    return principal


def require(scope: str):
    def check(principal: Annotated[Principal, Depends(authenticate)]):
        if scope not in principal.scopes:
            raise HTTPException(403, "Insufficient scope")
        return principal
    return check
