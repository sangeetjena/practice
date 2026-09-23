from ratings import RatingService


def main():
    """Run the agent-ratings demonstration using local objects.

    Called by: the script entry point.
    Returns: None; prints sample operation results.
    Example: python demo.py from the project directory.
    """
    service = RatingService()
    service.record("e1", "alice", 5)
    service.record("e2", "alice", 3)
    service.record("e3", "bob", 4)
    print("Replay:", service.record("e1", "alice", 5))
    for rating in service.rank():
        print(rating.agent_id, float(rating.average), rating.rating_count)


if __name__ == "__main__":
    main()
