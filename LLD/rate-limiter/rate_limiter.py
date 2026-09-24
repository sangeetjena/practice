"""Process-local, thread-safe rate limiting with injectable time and policies."""

import math
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Generic, Protocol, TypeVar


def positive_number(value: float, name: str) -> None:
    """Validate finite, bounded positive numeric input; raise ValueError otherwise.

    Called by: Policy constructors and cost/cleanup validation.
    Returns: None on success.
    Example: positive_number(5, "cost") succeeds; zero raises.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite positive number")
    if not 1e-9 <= value <= 1e12 or not math.isfinite(value):
        raise ValueError(f"{name} must be finite and between 1e-9 and 1e12")


@dataclass(frozen=True)
class Decision:
    """Immutable admission result; remaining/retry values are advisory under contention."""

    allowed: bool
    remaining: float
    retry_after_seconds: float


@dataclass
class CustomerState:
    """Private balance and timing state shared by fixed-window and token policies."""

    balance: int | Fraction
    updated_at: float
    last_seen_at: float


class TrackedState(Protocol):
    """Minimum state needed by the engine's idle cleanup, independent of algorithm."""

    last_seen_at: float


StateT = TypeVar("StateT", bound=TrackedState)


class Policy(Protocol[StateT]):
    """Strategy contract; each policy owns its state type and safe-expiry rules."""

    def validate_cost(self, cost: float) -> None:
        """Define policy-specific request-cost validation.

        Called by: RateLimiter.try_acquire before locking.
        Returns: None or a validation exception.
        Example: A fixed-window policy rejects cost=0.5.
        """
        ...

    def new_state(self, now: float) -> StateT:
        """Define initialization of a previously unseen customer's quota.

        Called by: RateLimiter.try_acquire under its lock.
        Returns: A mutable CustomerState.
        Example: A token bucket starts with its full capacity.
        """
        ...

    def acquire(self, state: StateT, now: float, cost: float) -> Decision:
        """Define atomic quota calculation and consumption; caller owns synchronization.

        Called by: RateLimiter.try_acquire.
        Returns: Decision with allowed, remaining and retry delay.
        Example: A cost of 1 consumes one available credit.
        """
        ...

    def can_forget(self, state: StateT, now: float) -> bool:
        """Define when discarding state cannot grant extra quota.

        Called by: RateLimiter.cleanup under its lock.
        Returns: bool indicating safe removal.
        Example: A fully refilled bucket is safe to forget.
        """
        ...


@dataclass(frozen=True)
class FixedWindow(Policy[CustomerState]):
    """Windows aligned to multiples of window_seconds on the supplied clock."""

    limit: int
    window_seconds: float

    def __post_init__(self) -> None:
        """Validate limit and duration after dataclass construction.

        Called by: Generated FixedWindow constructor.
        Returns: None; invalid configuration raises ValueError.
        Example: FixedWindow(10, 60) allows ten credits per minute.
        """
        if type(self.limit) is not int or not 1 <= self.limit <= 10**12:
            raise ValueError("limit must be an integer from 1 through 1e12")
        positive_number(self.window_seconds, "window_seconds")

    def validate_cost(self, cost: float) -> None:
        """Reject non-integral, nonpositive or over-limit request costs.

        Called by: RateLimiter.try_acquire.
        Returns: None on success.
        Example: FixedWindow(10, 60).validate_cost(2) succeeds.
        """
        positive_number(cost, "cost")
        if cost > self.limit or int(cost) != cost:
            raise ValueError("fixed-window cost must be an integer no greater than limit")

    def _start(self, now: float) -> float:
        # Decimal clock values such as 0.3 must belong to the [0.3, 0.4) window,
        # not the previous one because binary 0.3 / 0.1 is slightly below three.
        """Find the aligned window start using exact decimal arithmetic.

        Called by: new_state, acquire and can_forget.
        Returns: Window-start time as float.
        Example: FixedWindow(10, 60)._start(65) returns 60.0.
        """
        window = Fraction(str(self.window_seconds))
        return float((Fraction(str(now)) // window) * window)

    def new_state(self, now: float) -> CustomerState:
        """Create full quota for the window containing now.

        Called by: RateLimiter when a customer first appears.
        Returns: CustomerState with full balance and timestamps.
        Example: FixedWindow(10, 60).new_state(65).balance is 10.
        """
        return CustomerState(self.limit, self._start(now), now)

    def acquire(self, state: CustomerState, now: float, cost: float) -> Decision:
        """Reset expired quota, conditionally consume cost and update last-seen time.

        Called by: RateLimiter while holding its lock.
        Returns: Decision; also mutates supplied state.
        Example: From balance 10, acquire(state, 65, 2) allows and leaves 8.
        """
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
        """Check whether the stored window has expired.

        Called by: RateLimiter.cleanup.
        Returns: bool; no state mutation.
        Example: State from time 0 can be forgotten at time 60 for a 60-second window.
        """
        return self._start(now) > state.updated_at


@dataclass(frozen=True)
class TokenBucket(Policy[CustomerState]):
    """Continuously replenish bounded credits; initialize new customers full."""

    capacity: float
    refill_per_second: float

    def __post_init__(self) -> None:
        """Validate bucket capacity and refill rate.

        Called by: Generated TokenBucket constructor.
        Returns: None; invalid values raise ValueError.
        Example: TokenBucket(10, 2) refills two credits per second.
        """
        positive_number(self.capacity, "capacity")
        positive_number(self.refill_per_second, "refill_per_second")

    def validate_cost(self, cost: float) -> None:
        """Reject a cost that is invalid or larger than bucket capacity.

        Called by: RateLimiter.try_acquire.
        Returns: None on success.
        Example: TokenBucket(10, 2).validate_cost(0.5) succeeds.
        """
        positive_number(cost, "cost")
        if cost > self.capacity:
            raise ValueError("cost cannot exceed bucket capacity")

    def new_state(self, now: float) -> CustomerState:
        """Create a full bucket with exact fractional credit accounting.

        Called by: RateLimiter for a new customer.
        Returns: CustomerState.
        Example: TokenBucket(10, 2).new_state(0).balance equals 10.
        """
        return CustomerState(Fraction(str(self.capacity)), now, now)

    def _balance(self, state: CustomerState, now: float) -> Fraction:
        """Calculate capped refill without mutating state.

        Called by: acquire and can_forget.
        Returns: Exact Fraction balance.
        Example: Balance 3 at time 0 becomes 7 at time 2 with refill rate 2.
        """
        elapsed = Fraction(str(now)) - Fraction(str(state.updated_at))
        return min(
            Fraction(str(self.capacity)),
            state.balance + elapsed * Fraction(str(self.refill_per_second)),
        )

    def acquire(self, state: CustomerState, now: float, cost: float) -> Decision:
        """Apply refill and conditionally consume exact credits.

        Called by: RateLimiter while holding its lock.
        Returns: Decision and updated mutable state.
        Example: From a full capacity-10 bucket, cost 2 leaves 8 credits.
        """
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
        """Determine whether recreating full state would preserve quota.

        Called by: RateLimiter.cleanup.
        Returns: bool.
        Example: An empty capacity-10 bucket refilling at 2 is full after five seconds.
        """
        return self._balance(state, now) >= Fraction(str(self.capacity))


@dataclass
class SlidingLogState:
    """Ordered accepted timestamps; duplicates represent distinct simultaneous requests."""

    last_seen_at: float
    accepted_at: deque[Fraction] = field(default_factory=deque)


@dataclass(frozen=True)
class SlidingWindowLog(Policy[SlidingLogState]):
    """Exact unit-request cap in (now - window_seconds, now]; O(limit) state per key."""

    limit: int
    window_seconds: float

    def __post_init__(self) -> None:
        """Validate configuration, capping the per-key timestamp budget at 100,000."""
        if type(self.limit) is not int or not 1 <= self.limit <= 100_000:
            raise ValueError("sliding-log limit must be an integer from 1 through 100000")
        positive_number(self.window_seconds, "window_seconds")

    def validate_cost(self, cost: float) -> None:
        """Accept unit cost only; weighted logs require a different accounting contract."""
        positive_number(cost, "cost")
        if cost != 1:
            raise ValueError("sliding-log cost must equal one")

    def new_state(self, now: float) -> SlidingLogState:
        """Return an empty, independently allocated accepted-event deque."""
        return SlidingLogState(now)

    def acquire(self, state: SlidingLogState, now: float, cost: float) -> Decision:
        """Prune expired events, then record only an allowed request under the engine lock."""
        exact_now = Fraction(str(now))
        window = Fraction(str(self.window_seconds))
        cutoff = exact_now - window
        while state.accepted_at and state.accepted_at[0] <= cutoff:
            state.accepted_at.popleft()
        state.last_seen_at = now
        allowed = len(state.accepted_at) < self.limit
        if allowed:
            state.accepted_at.append(exact_now)
        retry = 0.0 if allowed else float(state.accepted_at[0] + window - exact_now)
        return Decision(allowed, self.limit - len(state.accepted_at), retry)

    def can_forget(self, state: SlidingLogState, now: float) -> bool:
        """Allow removal only when even the newest accepted event is outside the window."""
        return not state.accepted_at or state.accepted_at[-1] <= (
            Fraction(str(now)) - Fraction(str(self.window_seconds))
        )


class CustomerCapacityExceeded(RuntimeError):
    """No new customer can be tracked without discarding active quota state."""


class RateLimiter(Generic[StateT]):
    """One policy per instance. Every check/consume and cleanup is atomic.

    Policies run under the instance lock and must not block or call the limiter.
    Customer keys must include tenant/endpoint scope when required.
    """

    def __init__(
        self,
        policy: Policy[StateT],
        *,
        clock: Callable[[], float] = time.monotonic,
        max_customers: int = 100_000,
    ) -> None:
        """Create a process-local limiter with policy, clock and customer budget.

        Called by: Application startup or tests.
        Returns: None; construction produces a RateLimiter.
        Example: RateLimiter(TokenBucket(10, 2)) creates an initially empty registry.
        """
        if (
            isinstance(max_customers, bool)
            or not isinstance(max_customers, int)
            or max_customers <= 0
        ):
            raise ValueError("max_customers must be a positive integer")
        self._policy = policy
        self._clock = clock
        self._max_customers = max_customers
        self._states: dict[str, StateT] = {}
        self._lock = threading.Lock()
        self._last_clock_value = -math.inf

    def _now(self) -> float:
        """Read and validate the injected monotonic clock.

        Called by: try_acquire and cleanup under the lock.
        Returns: Finite time in seconds; invalid/backward clocks raise.
        Example: A test clock returning 5 produces 5.
        """
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
        """Atomically check and consume a customer's scoped quota.

        Called by: Request handler or demo before doing protected work.
        Returns: Decision; invalid input/capacity exhaustion raises.
        Example: limiter.try_acquire("tenant-a:alice") requests one credit.
        """
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
        """Remove idle customers only when reset would not grant extra quota.

        Called by: Periodic local maintenance or tests.
        Returns: Number of removed customer entries.
        Example: limiter.cleanup(60) removes safe entries idle at least a minute.

        Additional contract:
        Forget idle keys only when fresh state cannot grant extra quota.
        """
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
        """Read the number of currently tracked customers safely.

        Called by: Monitoring through property access, not a method call.
        Returns: int.
        Example: limiter.customer_count is 0 immediately after construction.
        """
        with self._lock:
            return len(self._states)
