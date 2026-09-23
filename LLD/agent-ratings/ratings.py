"""Concurrent in-memory ratings with exact ranking and bounded replay protection."""

from dataclasses import dataclass
from fractions import Fraction
from heapq import nsmallest
from threading import Lock


class Conflict(Exception):
    """An event ID was reused with another payload."""


class CapacityExceeded(Exception):
    """Configured storage budget exhausted; no mutation was performed."""


def _identifier(value: str, field: str) -> str:
    """Validate a case-sensitive event/agent identifier.

    Called by: record and get.
    Returns: The input string, or ValueError.
    Example: _identifier("agent-1", "agent_id") returns "agent-1".
    """
    if (
        not isinstance(value, str)
        or not value
        or len(value) > 128
        or value != value.strip()
        or any(ord(char) < 32 or ord(char) == 127 for char in value)
    ):
        raise ValueError(f"{field} must be a nonempty identifier of at most 128 characters")
    return value


@dataclass(frozen=True)
class AgentRating:
    agent_id: str
    total_score: int
    rating_count: int

    @property
    def average(self) -> Fraction:
        """Compute an exact average for comparison without float rounding.

        Called by: rank and consumers through property access.
        Returns: Fraction; rating_count must be positive.
        Example: AgentRating("a", 9, 2).average is Fraction(9, 2).
        """
        return Fraction(self.total_score, self.rating_count)


@dataclass(frozen=True)
class RecordResult:
    accepted: bool
    rating: AgentRating


class RatingService:
    """Ordering: average descending, count descending, agent ID ascending.

    All operations are synchronized. Event replay returns current aggregate with
    accepted=False, not the historical first response. No event eviction occurs:
    silently evicting IDs would weaken exactly-once contribution within this instance.
    """

    def __init__(self, *, max_events: int = 100_000, max_agents: int = 10_000) -> None:
        """Initialize bounded event replay tracking and agent totals.

        Called by: Application startup.
        Returns: None; construction produces RatingService.
        Example: RatingService(max_events=100) retains at most 100 distinct events.
        """
        if type(max_events) is not int or max_events < 1:
            raise ValueError("max_events must be a positive integer")
        if type(max_agents) is not int or max_agents < 1:
            raise ValueError("max_agents must be a positive integer")
        self._max_events, self._max_agents = max_events, max_agents
        self._events: dict[str, tuple[str, int]] = {}
        self._agents: dict[str, AgentRating] = {}
        self._lock = Lock()

    def record(self, event_id: str, agent_id: str, score: int) -> RecordResult:
        """Atomically count a new rating, accept identical replay as a no-op, reject conflicts.

        Called by: Rating ingestion or demo.
        Returns: RecordResult with accepted flag and current AgentRating.
        Example: record("e1", "a", 5) accepts once; identical replay has accepted=False.
        """
        _identifier(event_id, "event_id")
        _identifier(agent_id, "agent_id")
        if type(score) is not int or not 1 <= score <= 5:
            raise ValueError("score must be an integer from 1 through 5")
        payload = (agent_id, score)
        with self._lock:
            if event_id in self._events:
                if self._events[event_id] != payload:
                    raise Conflict("event ID already has another payload")
                return RecordResult(False, self._agents[agent_id])
            if len(self._events) >= self._max_events:
                raise CapacityExceeded("event budget exhausted")
            previous = self._agents.get(agent_id)
            if previous is None and len(self._agents) >= self._max_agents:
                raise CapacityExceeded("agent budget exhausted")
            total = (previous.total_score if previous else 0) + score
            count = (previous.rating_count if previous else 0) + 1
            aggregate = AgentRating(agent_id, total, count)
            self._events[event_id] = payload
            self._agents[agent_id] = aggregate
            return RecordResult(True, aggregate)

    def get(self, agent_id: str) -> AgentRating | None:
        """Read one immutable agent aggregate under the lock.

        Called by: Reporting caller.
        Returns: AgentRating or None.
        Example: service.get("unknown") returns None.
        """
        _identifier(agent_id, "agent_id")
        with self._lock:
            return self._agents.get(agent_id)

    def rank(self, *, limit: int = 10) -> tuple[AgentRating, ...]:
        """Rank a detached snapshot by average, count, then agent ID.

        Called by: Leaderboard caller.
        Returns: Tuple of up to limit AgentRating values.
        Example: service.rank(limit=3) returns the top three available agents.
        """
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError("limit must be an integer from 1 through 1000")
        with self._lock:
            snapshot = tuple(self._agents.values())
        # Immutable values allow ranking outside the mutation critical section.
        return tuple(
            nsmallest(
                limit,
                snapshot,
                key=lambda rating: (-rating.average, -rating.rating_count, rating.agent_id),
            )
        )
