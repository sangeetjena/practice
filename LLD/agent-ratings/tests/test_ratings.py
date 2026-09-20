import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from fractions import Fraction
from threading import Barrier

from ratings import CapacityExceeded, Conflict, RatingService


class RatingTest(unittest.TestCase):
    def test_weighted_average(self):
        service = RatingService()
        for index, score in enumerate([5, 5, 2]):
            service.record(str(index), "alice", score)
        self.assertEqual(Fraction(4), service.get("alice").average)

    def test_ties_count_then_id(self):
        service = RatingService()
        for event, agent, score in [
            ("1", "zoe", 4),
            ("2", "alice", 5),
            ("3", "alice", 3),
            ("4", "bob", 4),
            ("5", "top", 5),
        ]:
            service.record(event, agent, score)
        self.assertEqual(["top", "alice", "bob", "zoe"], [x.agent_id for x in service.rank()])

    def test_replay_and_conflicting_event(self):
        service = RatingService()
        self.assertTrue(service.record("1", "alice", 4).accepted)
        self.assertFalse(service.record("1", "alice", 4).accepted)
        with self.assertRaises(Conflict):
            service.record("1", "alice", 5)
        self.assertEqual(1, service.get("alice").rating_count)

    def test_capacity_rejects_without_mutation_but_allows_replay(self):
        service = RatingService(max_events=1)
        service.record("1", "alice", 4)
        with self.assertRaises(CapacityExceeded):
            service.record("2", "bob", 3)
        self.assertIsNone(service.get("bob"))
        self.assertFalse(service.record("1", "alice", 4).accepted)

    def test_agent_capacity_still_allows_existing_agent(self):
        service = RatingService(max_agents=1)
        service.record("1", "alice", 4)
        with self.assertRaises(CapacityExceeded):
            service.record("2", "bob", 3)
        self.assertTrue(service.record("2", "alice", 3).accepted)

    def test_invalid_inputs(self):
        service = RatingService()
        for score in (0, 6, True, 1.5, "5"):
            with self.assertRaises(ValueError):
                service.record("event", "alice", score)
        for identifier in ("", " a", "a\n", "a\x7f", None):
            with self.assertRaises(ValueError):
                service.record(identifier, "alice", 3)
        for limit in (0, 1001, True):
            with self.assertRaises(ValueError):
                service.rank(limit=limit)

    def test_snapshot_values_immutable(self):
        service = RatingService()
        result = service.record("1", "alice", 3)
        with self.assertRaises(FrozenInstanceError):
            result.rating.rating_count = 100
        service.record("2", "alice", 5)
        self.assertEqual(1, result.rating.rating_count)

    def test_empty_and_top_k(self):
        service = RatingService()
        self.assertEqual((), service.rank())
        self.assertIsNone(service.get("absent"))
        for index in range(20):
            service.record(str(index), str(index), 5)
        self.assertEqual(3, len(service.rank(limit=3)))

    def test_concurrent_replay_contributes_once(self):
        service = RatingService()
        barrier = Barrier(8)

        def record(_):
            barrier.wait(timeout=5)
            return service.record("same", "alice", 5).accepted

        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(1, sum(pool.map(record, range(8))))
        self.assertEqual(1, service.get("alice").rating_count)

    def test_concurrent_distinct_events_no_lost_updates(self):
        service = RatingService()
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(lambda i: service.record(str(i), "alice", i % 5 + 1), range(500)))
        self.assertEqual(500, service.get("alice").rating_count)
        self.assertEqual(1500, service.get("alice").total_score)

    def test_concurrent_reads_are_consistent(self):
        service = RatingService()

        def work(index):
            service.record(str(index), "alice", 5)
            rating = service.rank()[0]
            self.assertEqual(rating.rating_count * 5, rating.total_score)

        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(work, range(100)))


if __name__ == "__main__":
    unittest.main()
