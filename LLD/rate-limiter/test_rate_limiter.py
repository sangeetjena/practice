import concurrent.futures
import threading
import unittest

from rate_limiter import CustomerCapacityExceeded, FixedWindow, RateLimiter, TokenBucket


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


class RateLimiterTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()

    def test_fixed_window_boundary_and_independent_customers(self):
        limiter = RateLimiter(FixedWindow(2, 10), clock=self.clock)
        self.assertTrue(limiter.try_acquire("a", 2).allowed)
        self.assertFalse(limiter.try_acquire("a").allowed)
        self.assertTrue(limiter.try_acquire("b").allowed)
        self.clock.now = 9.5
        self.assertEqual(limiter.try_acquire("a").retry_after_seconds, 0.5)
        self.clock.now = 10
        self.assertTrue(limiter.try_acquire("a", 2).allowed)

    def test_token_refill_rejection_and_cap(self):
        limiter = RateLimiter(TokenBucket(4, 2), clock=self.clock)
        self.assertTrue(limiter.try_acquire("a", 4).allowed)
        decision = limiter.try_acquire("a")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.retry_after_seconds, 0.5)
        self.clock.now = 0.5
        self.assertTrue(limiter.try_acquire("a").allowed)
        self.clock.now = 1000
        self.assertEqual(limiter.try_acquire("a").remaining, 3)

    def test_fractional_bucket_cost(self):
        limiter = RateLimiter(TokenBucket(1, 1), clock=self.clock)
        self.assertEqual(limiter.try_acquire("a", 0.25).remaining, 0.75)

    def test_small_cost_cannot_disappear_from_large_balance(self):
        limiter = RateLimiter(TokenBucket(1e12, 1), clock=self.clock)
        self.assertTrue(limiter.try_acquire("a", 1e-9).allowed)
        self.assertFalse(limiter.try_acquire("a", 1e12).allowed)

    def test_decimal_window_boundary(self):
        limiter = RateLimiter(FixedWindow(1, 0.1), clock=self.clock)
        self.clock.now = 0.2
        self.assertTrue(limiter.try_acquire("a").allowed)
        self.clock.now = 0.3
        self.assertTrue(limiter.try_acquire("a").allowed)
        self.assertFalse(limiter.try_acquire("a").allowed)

    def test_decimal_refill_boundary(self):
        limiter = RateLimiter(TokenBucket(0.3, 0.1), clock=self.clock)
        for _ in range(3):
            self.assertTrue(limiter.try_acquire("a", 0.1).allowed)
        self.assertFalse(limiter.try_acquire("a", 0.1).allowed)
        self.clock.now = 1
        self.assertTrue(limiter.try_acquire("a", 0.1).allowed)

    def test_oversized_clock_rejected_without_overflow(self):
        limiter = RateLimiter(FixedWindow(1, 1), clock=self.clock)
        self.clock.now = 10**400
        with self.assertRaises(ValueError):
            limiter.try_acquire("a")
        self.assertEqual(0, limiter.customer_count)

    def test_concurrent_check_consume_is_atomic(self):
        for policy in (FixedWindow(17, 10), TokenBucket(17, 1)):
            with self.subTest(policy=policy):
                limiter = RateLimiter(policy, clock=self.clock)
                barrier = threading.Barrier(32)

                def acquire(_):
                    barrier.wait()
                    return limiter.try_acquire("a").allowed

                with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                    self.assertEqual(sum(executor.map(acquire, range(32))), 17)

    def test_cleanup_does_not_reset_active_quota(self):
        for policy in (FixedWindow(1, 10), TokenBucket(1, 0.1)):
            limiter = RateLimiter(policy, clock=self.clock)
            self.clock.now = 0
            limiter.try_acquire("a")
            self.clock.now = 5
            self.assertEqual(limiter.cleanup(1), 0)
            self.assertFalse(limiter.try_acquire("a").allowed)
            self.clock.now = 10
            self.assertEqual(limiter.cleanup(1), 1)
            self.assertTrue(limiter.try_acquire("a").allowed)

    def test_cleanup_racing_requests_cannot_reset_active_state(self):
        limiter = RateLimiter(FixedWindow(7, 100), clock=self.clock)
        self.clock.now = 10

        def work(index):
            if index % 2:
                return limiter.try_acquire("a").allowed
            limiter.cleanup(1)
            return False

        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            self.assertEqual(sum(executor.map(work, range(200))), 7)

    def test_capacity_does_not_evict_existing_customer(self):
        limiter = RateLimiter(FixedWindow(1, 10), clock=self.clock, max_customers=1)
        limiter.try_acquire("a")
        with self.assertRaises(CustomerCapacityExceeded):
            limiter.try_acquire("b")
        self.assertFalse(limiter.try_acquire("a").allowed)
        self.assertEqual(limiter.customer_count, 1)

    def test_invalid_configuration_and_cost(self):
        for value in (0, -1, float("nan"), float("inf"), True, "2"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    TokenBucket(value, 1)
                with self.assertRaises(ValueError):
                    FixedWindow(1, value)
        limiter = RateLimiter(FixedWindow(2, 10), clock=self.clock)
        for cost in (0, -1, 3, 0.5, float("nan")):
            with self.assertRaises(ValueError):
                limiter.try_acquire("a", cost)
        self.assertEqual(limiter.customer_count, 0)

    def test_bad_keys_and_clock(self):
        limiter = RateLimiter(FixedWindow(2, 10), clock=self.clock)
        for key in ("", " ", "a" * 513, None):
            with self.assertRaises(ValueError):
                limiter.try_acquire(key)
        self.clock.now = 5
        limiter.try_acquire("a")
        self.clock.now = 4
        with self.assertRaises(ValueError):
            limiter.try_acquire("a")
        self.clock.now = float("nan")
        with self.assertRaises(ValueError):
            limiter.try_acquire("a")


if __name__ == "__main__":
    unittest.main()
