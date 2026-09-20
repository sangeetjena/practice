"""Process-local, thread-safe rate limiting with injectable time and policies."""

import math
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from typing import Protocol


def positive_number(value: float, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite positive number")
    if not 1e-9 <= value <= 1e12 or not math.isfinite(value):
        raise ValueError(f"{name} must be finite and between 1e-9 and 1e12")


@dataclass(frozen=True)
class Decision:
    allowed: bool
    remaining: float
    retry_after_seconds: float


@dataclass
class CustomerState:
    balance: int | Fraction
    updated_at: float
    last_seen_at: float


class Policy(Protocol):
    def validate_cost(self, cost: float) -> None: ...
    def new_state(self, now: float) -> CustomerState: ...
    def acquire(self, state: CustomerState, now: float, cost: float) -> Decision: ...
    def can_forget(self, state: CustomerState, now: float) -> bool: ...


@dataclass(frozen=True)
class FixedWindow:
    """Windows aligned to multiples of window_seconds on the supplied clock."""

    limit: int
    window_seconds: float

    def __post_init__(self) -> None:
        if type(self.limit) is not int or not 1 <= self.limit <= 10**12:
            raise ValueError("limit must be an integer from 1 through 1e12")
        positive_number(self.window_seconds, "window_seconds")

    def validate_cost(self, cost: float) -> None:
        positive_number(cost, "cost")
        if cost > self.limit or int(cost) != cost:
            raise ValueError("fixed-window cost must be an integer no greater than limit")

    def _start(self, now: float) -> float:
        # Decimal clock values such as 0.3 must belong to the [0.3, 0.4) window,
        # not the previous one because binary 0.3 / 0.1 is slightly below three.
        window = Fraction(str(self.window_seconds))
        return float((Fraction(str(now)) // window) * window)

    def new_state(self, now: float) -> CustomerState:
        return CustomerState(self.limit, self._start(now), now)

    def acquire(self, state: CustomerState, now: float, cost: float) -> Decision:
        start = self._start(now)
        if start > state.updated_at:
            state.balance = self.limit
            state.updated_at = start
        allowed = state.balance >= cost
        if allowed:
            state.balance -= int(cost)
        state.last_seen_at = now
        retry_after = 0.0 if allowed else max(0.0, start + self.window_seconds - now)
        return Decision(allowed, state.balance, retry_after)

    def can_forget(self, state: CustomerState, now: float) -> bool:
        return self._start(now) > state.updated_at


@dataclass(frozen=True)
class TokenBucket:
    """Continuously replenish bounded credits; initialize new customers full."""

    capacity: float
    refill_per_second: float

    def __post_init__(self) -> None:
        positive_number(self.capacity, "capacity")
        positive_number(self.refill_per_second, "refill_per_second")

    def validate_cost(self, cost: float) -> None:
        positive_number(cost, "cost")
        if cost > self.capacity:
            raise ValueError("cost cannot exceed bucket capacity")

    def new_state(self, now: float) -> CustomerState:
        return CustomerState(Fraction(str(self.capacity)), now, now)

    def _balance(self, state: CustomerState, now: float) -> Fraction:
        elapsed = Fraction(str(now)) - Fraction(str(state.updated_at))
        return min(
            Fraction(str(self.capacity)),
            state.balance + elapsed * Fraction(str(self.refill_per_second)),
        )

    def acquire(self, state: CustomerState, now: float, cost: float) -> Decision:
        state.balance = self._balance(state, now)
        state.updated_at = now
        state.last_seen_at = now
        exact_cost = Fraction(str(cost))
        allowed = state.balance >= exact_cost
        if allowed:
            state.balance -= exact_cost
        retry_after = (
            0.0
            if allowed
            else float((exact_cost - state.balance) / Fraction(str(self.refill_per_second)))
        )
        return Decision(allowed, float(state.balance), retry_after)

    def can_forget(self, state: CustomerState, now: float) -> bool:
        return self._balance(state, now) >= Fraction(str(self.capacity))


class CustomerCapacityExceeded(RuntimeError):
    """No new customer can be tracked without discarding active quota state."""


class RateLimiter:
    """One policy per instance. Every check/consume and cleanup is atomic.

    Policies run under the instance lock and must not block or call the limiter.
    Customer keys must include tenant/endpoint scope when required.
    """

    def __init__(
        self,
        policy: Policy,
        *,
        clock: Callable[[], float] = time.monotonic,
        max_customers: int = 100_000,
    ) -> None:
        if (
            isinstance(max_customers, bool)
            or not isinstance(max_customers, int)
            or max_customers <= 0
        ):
            raise ValueError("max_customers must be a positive integer")
        self._policy = policy
        self._clock = clock
        self._max_customers = max_customers
        self._states: dict[str, CustomerState] = {}
        self._lock = threading.Lock()
        self._last_clock_value = -math.inf

    def _now(self) -> float:
        now = self._clock()
        if (
            not isinstance(now, (int, float))
            or isinstance(now, bool)
            or not 0 <= now <= 1e12
            or not math.isfinite(now)
        ):
            raise ValueError("clock must return finite seconds between zero and 1e12")
        if now < self._last_clock_value:
            raise ValueError("clock must be monotonic")
        self._last_clock_value = now
        return now

    def try_acquire(self, customer_key: str, cost: float = 1) -> Decision:
        if not isinstance(customer_key, str) or not customer_key.strip() or len(customer_key) > 512:
            raise ValueError("customer_key must be nonblank and at most 512 characters")
        self._policy.validate_cost(cost)
        with self._lock:
            now = self._now()
            state = self._states.get(customer_key)
            if state is None:
                if len(self._states) >= self._max_customers:
                    raise CustomerCapacityExceeded("run cleanup or provision additional capacity")
                state = self._policy.new_state(now)
                self._states[customer_key] = state
            return self._policy.acquire(state, now, cost)

    def cleanup(self, idle_seconds: float) -> int:
        """Forget idle keys only when fresh state cannot grant extra quota."""
        positive_number(idle_seconds, "idle_seconds")
        with self._lock:
            now = self._now()
            expired = [
                key
                for key, state in self._states.items()
                if now - state.last_seen_at >= idle_seconds and self._policy.can_forget(state, now)
            ]
            for key in expired:
                del self._states[key]
            return len(expired)

    @property
    def customer_count(self) -> int:
        with self._lock:
            return len(self._states)
