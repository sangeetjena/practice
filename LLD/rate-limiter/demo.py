from rate_limiter import FixedWindow, RateLimiter, TokenBucket


def main() -> None:
    """Run the rate-limiter demonstration using local objects.

    Called by: the script entry point.
    Returns: None; prints sample operation results.
    Example: python demo.py from the project directory.
    """
    now = [0.0]
    for policy in (FixedWindow(2, 10), TokenBucket(2, 0.5)):
        now[0] = 0.0
        limiter = RateLimiter(policy, clock=lambda: now[0])
        print(type(policy).__name__)
        for _ in range(3):
            print(limiter.try_acquire("tenant-a:customer-1"))
        now[0] = 10.0
        print("After 10 seconds:", limiter.try_acquire("tenant-a:customer-1"))


if __name__ == "__main__":
    main()
