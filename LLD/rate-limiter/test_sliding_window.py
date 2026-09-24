"""Deterministic rolling-window boundary, cleanup, and concurrency tests."""

import concurrent.futures
import random
import threading
import unittest
from fractions import Fraction

from rate_limiter import CustomerCapacityExceeded, RateLimiter, SlidingWindowLog
from test_rate_limiter import FakeClock


class SlidingWindowTests(unittest.TestCase):
    """Exercise observable contracts without sleeping or relying on wall-clock timing."""

    def setUp(self):
        """Give every test its own monotonic clock and three-per-ten-second limiter."""
        self.clock = FakeClock()
        self.limiter = RateLimiter(SlidingWindowLog(3, 10), clock=self.clock)

    def test_rolling_boundary_and_retry(self):
        """Expire the lower boundary inclusively while retaining more recent events."""
        for now in (0, 2, 9):
            self.clock.now = now
            self.assertTrue(self.limiter.try_acquire("a").allowed)
        self.clock.now = 9.5
        self.assertEqual(self.limiter.try_acquire("a").retry_after_seconds, 0.5)
        self.clock.now = 10
        self.assertTrue(self.limiter.try_acquire("a").allowed)
        self.assertFalse(self.limiter.try_acquire("a").allowed)

    def test_same_timestamp_requests_remain_distinct(self):
        """Three simultaneous admissions must occupy three slots, not overwrite one."""
        for remaining in (2, 1, 0):
            self.assertEqual(self.limiter.try_acquire("a").remaining, remaining)
        self.assertFalse(self.limiter.try_acquire("a").allowed)
        self.assertEqual(self.limiter.try_acquire("b").remaining, 2)

    def test_denial_does_not_extend_window(self):
        """Repeated rejected attempts must not be added to the accepted-event log."""
        for _ in range(3):
            self.limiter.try_acquire("a")
        self.clock.now = 9
        for _ in range(50):
            self.assertFalse(self.limiter.try_acquire("a").allowed)
        self.clock.now = 10
        self.assertEqual(self.limiter.try_acquire("a").remaining, 2)

    def test_decimal_boundary(self):
        """An event at 0.2 expires at 0.3 for a supplied decimal window of 0.1."""
        limiter = RateLimiter(SlidingWindowLog(1, 0.1), clock=self.clock)
        self.clock.now = 0.2
        limiter.try_acquire("a")
        self.clock.now = 0.3
        self.assertTrue(limiter.try_acquire("a").allowed)

    def test_cleanup_waits_for_newest_event(self):
        """Deleting idle state while one accepted event is live would mint quota."""
        self.limiter.try_acquire("a")
        self.clock.now = 9
        self.limiter.try_acquire("a")
        self.clock.now = 10
        self.assertEqual(self.limiter.cleanup(1), 0)
        self.clock.now = 19
        self.assertEqual(self.limiter.cleanup(1), 1)
        self.assertEqual(self.limiter.customer_count, 0)

    def test_concurrent_admissions_and_cleanup(self):
        """Admissions and cleanup must use the same lock and admit exactly the quota."""
        barrier = threading.Barrier(24)

        def acquire(_):
            """Start competing workers together and run safe cleanup before admission."""
            barrier.wait()
            self.limiter.cleanup(1)
            return self.limiter.try_acquire("a").allowed

        with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
            self.assertEqual(sum(executor.map(acquire, range(24))), 3)

    def test_reject_invalid_configuration_and_cost_without_state(self):
        """Bound configuration and reject unsupported weighted costs before insertion."""
        for value in (0, -1, True, 1.5, 100_001):
            with self.assertRaises(ValueError):
                SlidingWindowLog(value, 10)
        for value in (0, -1, float("nan"), float("inf"), True):
            with self.assertRaises(ValueError):
                SlidingWindowLog(1, value)
        for cost in (0, -1, 0.5, 2, True, float("nan")):
            with self.assertRaises(ValueError):
                self.limiter.try_acquire("a", cost)
        self.assertEqual(self.limiter.customer_count, 0)

    def test_capacity_preserves_existing_quota(self):
        """Memory exhaustion rejects a new identity without resetting existing state."""
        limiter = RateLimiter(SlidingWindowLog(1, 10), clock=self.clock, max_customers=1)
        limiter.try_acquire("a")
        with self.assertRaises(CustomerCapacityExceeded):
            limiter.try_acquire("b")
        self.assertFalse(limiter.try_acquire("a").allowed)

    def test_random_trace_matches_independent_list_model(self):
        """Compare 1,000 arrivals/cleanups with an unoptimized integer-millisecond oracle."""
        rng = random.Random(41)
        limiter = RateLimiter(SlidingWindowLog(7, 1), clock=self.clock)
        accepted = {"a": [], "b": []}
        now_ms = 0
        for _ in range(1000):
            now_ms += rng.randrange(50)
            self.clock.now = now_ms / 1000
            key = rng.choice(("a", "b"))
            accepted[key] = [t for t in accepted[key] if t > now_ms - 1000]
            expected = len(accepted[key]) < 7
            if expected:
                accepted[key].append(now_ms)
            decision = limiter.try_acquire(key)
            self.assertEqual(decision.allowed, expected)
            self.assertEqual(decision.remaining, 7 - len(accepted[key]))
            if not expected:
                self.assertEqual(
                    decision.retry_after_seconds,
                    float(Fraction(accepted[key][0] + 1000 - now_ms, 1000)),
                )
            if rng.randrange(5) == 0:
                limiter.cleanup(0.1)


if __name__ == "__main__":
    unittest.main()
