import concurrent.futures
import threading
import unittest

from rate_limiter import CustomerCapacityExceeded, FixedWindow, RateLimiter, TokenBucket


class FakeClock:
    def __init__(self):
        """Initialize a deterministic test clock at zero seconds.

        Called by: the enclosing test or its thread-pool callback.
        Returns: None; assertions raise on failure.
        Example (with test-local values): FakeClock().now is 0.0.
        """
        self.now = 0.0

    def __call__(self):
        """Read manually controlled time instead of sleeping.

        Called by: the enclosing test or its thread-pool callback.
        Returns: self.now.
        Example (with test-local values): clock() returns clock.now.
        """
        return self.now


class RateLimiterTests(unittest.TestCase):
    def setUp(self):
        """Prepare fresh state for each test so cases do not share mutations.

        Called by: unittest before each test case.
        Returns: None; assertions raise on failure.
        Example (with test-local values): FakeClock()
        """
        self.clock = FakeClock()

    def test_fixed_window_boundary_and_independent_customers(self):
        """Verify the scenario: fixed window boundary and independent customers.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertTrue(limiter.try_acquire('a', 2).allowed)
        """
        limiter = RateLimiter(FixedWindow(2, 10), clock=self.clock)
        self.assertTrue(limiter.try_acquire("a", 2).allowed)
        self.assertFalse(limiter.try_acquire("a").allowed)
        self.assertTrue(limiter.try_acquire("b").allowed)
        self.clock.now = 9.5
        self.assertEqual(limiter.try_acquire("a").retry_after_seconds, 0.5)
        self.clock.now = 10
        self.assertTrue(limiter.try_acquire("a", 2).allowed)

    def test_token_refill_rejection_and_cap(self):
        """Verify the scenario: token refill rejection and cap.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertTrue(limiter.try_acquire('a', 4).allowed)
        """
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
        """Verify the scenario: fractional bucket cost.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(limiter.try_acquire('a', 0.25).remaining, 0.75)
        """
        limiter = RateLimiter(TokenBucket(1, 1), clock=self.clock)
        self.assertEqual(limiter.try_acquire("a", 0.25).remaining, 0.75)

    def test_small_cost_cannot_disappear_from_large_balance(self):
        """Verify the scenario: small cost cannot disappear from large balance.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertTrue(limiter.try_acquire('a', 1e-09).allowed)
        """
        limiter = RateLimiter(TokenBucket(1e12, 1), clock=self.clock)
        self.assertTrue(limiter.try_acquire("a", 1e-9).allowed)
        self.assertFalse(limiter.try_acquire("a", 1e12).allowed)

    def test_decimal_window_boundary(self):
        """Verify the scenario: decimal window boundary.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertTrue(limiter.try_acquire('a').allowed)
        """
        limiter = RateLimiter(FixedWindow(1, 0.1), clock=self.clock)
        self.clock.now = 0.2
        self.assertTrue(limiter.try_acquire("a").allowed)
        self.clock.now = 0.3
        self.assertTrue(limiter.try_acquire("a").allowed)
        self.assertFalse(limiter.try_acquire("a").allowed)

    def test_decimal_refill_boundary(self):
        """Verify the scenario: decimal refill boundary.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertFalse(limiter.try_acquire('a', 0.1).allowed)
        """
        limiter = RateLimiter(TokenBucket(0.3, 0.1), clock=self.clock)
        for _ in range(3):
            self.assertTrue(limiter.try_acquire("a", 0.1).allowed)
        self.assertFalse(limiter.try_acquire("a", 0.1).allowed)
        self.clock.now = 1
        self.assertTrue(limiter.try_acquire("a", 0.1).allowed)

    def test_oversized_clock_rejected_without_overflow(self):
        """Verify the scenario: oversized clock rejected without overflow.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(0, limiter.customer_count)
        """
        limiter = RateLimiter(FixedWindow(1, 1), clock=self.clock)
        self.clock.now = 10**400
        with self.assertRaises(ValueError):
            limiter.try_acquire("a")
        self.assertEqual(0, limiter.customer_count)

    def test_concurrent_check_consume_is_atomic(self):
        """Verify the scenario: concurrent check consume is atomic.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(sum(executor.map(acquire, range(32))), 17)
        """
        for policy in (FixedWindow(17, 10), TokenBucket(17, 1)):
            with self.subTest(policy=policy):
                limiter = RateLimiter(policy, clock=self.clock)
                barrier = threading.Barrier(32)

                def acquire(_):
                    """Synchronize request admission to test atomic quota consumption.

                    Called by: the enclosing test or its thread-pool callback.
                    Returns: limiter.try_acquire('a').allowed.
                    Example (with test-local values): barrier.wait()
                    """
                    barrier.wait()
                    return limiter.try_acquire("a").allowed

                with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                    self.assertEqual(sum(executor.map(acquire, range(32))), 17)

    def test_cleanup_does_not_reset_active_quota(self):
        """Verify the scenario: cleanup does not reset active quota.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(limiter.cleanup(1), 0)
        """
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
        """Verify the scenario: cleanup racing requests cannot reset active state.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(sum(executor.map(work, range(200))), 7)
        """
        limiter = RateLimiter(FixedWindow(7, 100), clock=self.clock)
        self.clock.now = 10

        def work(index):
            """Execute one indexed operation in the enclosing concurrency scenario.

            Called by: the enclosing test or its thread-pool callback.
            Returns: False; otherwise limiter.try_acquire('a').allowed.
            Example (with test-local values): limiter.cleanup(1)
            """
            if index % 2:
                return limiter.try_acquire("a").allowed
            limiter.cleanup(1)
            return False

        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            self.assertEqual(sum(executor.map(work, range(200))), 7)

    def test_capacity_does_not_evict_existing_customer(self):
        """Verify the scenario: capacity does not evict existing customer.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertFalse(limiter.try_acquire('a').allowed)
        """
        limiter = RateLimiter(FixedWindow(1, 10), clock=self.clock, max_customers=1)
        limiter.try_acquire("a")
        with self.assertRaises(CustomerCapacityExceeded):
            limiter.try_acquire("b")
        self.assertFalse(limiter.try_acquire("a").allowed)
        self.assertEqual(limiter.customer_count, 1)

    def test_invalid_configuration_and_cost(self):
        """Verify the scenario: invalid configuration and cost.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(limiter.customer_count, 0)
        """
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
        """Verify the scenario: bad keys and clock.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertRaises(ValueError)
        """
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
