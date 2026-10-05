from datetime import datetime
from typing import Protocol

from pydantic import BaseModel

from stock_research.domain.models import EvidenceRef


class Candidate(BaseModel):
    symbol: str
    theme_id: str
    as_of: datetime
    evidence: list[EvidenceRef]
    reason: str


class Theme(Protocol):
    theme_id: str
    version: str

    async def discover(self, as_of: datetime) -> list[Candidate]: ...
