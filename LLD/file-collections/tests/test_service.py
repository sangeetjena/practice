import random
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from threading import Barrier

from file_collections import CapacityExceeded, FileCollections, FileRecord, VersionConflict


class CollectionTests(unittest.TestCase):
    def setUp(self):
        """Prepare fresh state for each test so cases do not share mutations.

        Called by: unittest before each test case.
        Returns: None; assertions raise on failure.
        Example (with test-local values): FileCollections()
        """
        self.service = FileCollections()

    def assert_consistent(self, snapshot):
        """Recompute accounting from snapshot records and assert aggregate invariants.

        Called by: the enclosing test or its thread-pool callback.
        Returns: None; assertions raise on failure.
        Example (with test-local values): self.assertEqual(snapshot.total_size_bytes, sum((file.size_bytes for file in snapshot.files)))
        """
        self.assertEqual(snapshot.total_size_bytes, sum(file.size_bytes for file in snapshot.files))
        sizes, counts = {}, {}
        for file in snapshot.files:
            for collection in file.collection_ids:
                sizes[collection] = sizes.get(collection, 0) + file.size_bytes
                counts[collection] = counts.get(collection, 0) + 1
        self.assertEqual({c.collection_id: c.size_bytes for c in snapshot.collections}, sizes)
        self.assertEqual({c.collection_id: c.file_count for c in snapshot.collections}, counts)

    def test_unique_storage_and_duplicate_memberships(self):
        """Verify the scenario: unique storage and duplicate memberships.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(self.service.snapshot().total_size_bytes, 30)
        """
        self.service.upsert(FileRecord("a", 20, ["x", "x", "y"]))
        self.service.upsert(FileRecord("b", 10))
        self.assertEqual(self.service.snapshot().total_size_bytes, 30)
        self.assertEqual([c.size_bytes for c in self.service.top_k(9)], [20, 20])
        self.assert_consistent(self.service.snapshot())

    def test_replace_resize_and_delete(self):
        """Verify the scenario: replace resize and delete.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(self.service.snapshot().total_size_bytes, 7)
        """
        self.service.upsert(FileRecord("a", 20, {"x", "y"}))
        self.service.upsert(FileRecord("a", 7, {"z"}))
        self.assertEqual(self.service.snapshot().total_size_bytes, 7)
        self.assertEqual([c.collection_id for c in self.service.top_k(9)], ["z"])
        self.assertTrue(self.service.delete("a"))
        self.assertFalse(self.service.delete("a"))
        self.assertEqual(self.service.snapshot().collections, ())

    def test_zero_byte_collection_retained_until_last_member_removed(self):
        """Verify the scenario: zero byte collection retained until last member removed.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(self.service.top_k(1)[0].file_count, 1)
        """
        self.service.upsert(FileRecord("a", 0, {"x"}))
        self.assertEqual(self.service.top_k(1)[0].file_count, 1)
        self.service.delete("a")
        self.assertEqual(self.service.top_k(1), ())

    def test_deterministic_ranking_and_k_boundaries(self):
        """Verify the scenario: deterministic ranking and k boundaries.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual([c.collection_id for c in self.service.top_k(2)], ['a', 'b'])
        """
        for name, size in [("z", 2), ("b", 10), ("a", 10)]:
            self.service.upsert(FileRecord(name, size, {name}))
        self.assertEqual([c.collection_id for c in self.service.top_k(2)], ["a", "b"])
        self.assertEqual(self.service.top_k(0), ())
        self.assertEqual(len(self.service.top_k(20)), 3)
        with self.assertRaises(ValueError):
            self.service.top_k(-1)
        with self.assertRaises(TypeError):
            self.service.top_k(True)

    def test_version_and_idempotency(self):
        """Verify the scenario: version and idempotency.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(self.service.upsert(file, expected_version=0), 1)
        """
        file = FileRecord("a", 1)
        self.assertEqual(self.service.upsert(file, expected_version=0), 1)
        self.assertEqual(self.service.upsert(file), 1)
        with self.assertRaises(VersionConflict):
            self.service.upsert(FileRecord("a", 2), expected_version=0)
        with self.assertRaises(VersionConflict):
            self.service.delete("a", expected_version=0)
        self.assertEqual(self.service.snapshot().total_size_bytes, 1)

    def test_storage_budget_is_checked_before_replacement(self):
        """Verify the scenario: storage budget is checked before replacement.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(before, service.snapshot())
        """
        service = FileCollections(max_files=1, max_memberships=1)
        service.upsert(FileRecord("a", 5, {"x"}))
        before = service.snapshot()
        with self.assertRaises(CapacityExceeded):
            service.upsert(FileRecord("b", 2))
        with self.assertRaises(CapacityExceeded):
            service.upsert(FileRecord("a", 10, {"x", "y"}))
        self.assertEqual(before, service.snapshot())
        service.delete("a")
        service.upsert(FileRecord("b", 2, {"y"}))
        self.assert_consistent(service.snapshot())

    def test_membership_input_is_bounded(self):
        """Verify the scenario: membership input is bounded.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(frozenset({'x'}), FileRecord('a', 1, ['x'] * 1000).collection_ids)
        """
        with self.assertRaises(ValueError):
            FileRecord("a", 1, ["x"] * 1001)
        self.assertEqual(frozenset({"x"}), FileRecord("a", 1, ["x"] * 1000).collection_ids)

    def test_snapshots_and_inputs_are_immutable(self):
        """Verify the scenario: snapshots and inputs are immutable.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(before.files[0].collection_ids, frozenset({'x'}))
        """
        memberships = {"x"}
        self.service.upsert(FileRecord("a", 1, memberships))
        before = self.service.snapshot()
        memberships.add("y")
        self.service.delete("a")
        self.assertEqual(before.files[0].collection_ids, frozenset({"x"}))
        with self.assertRaises(FrozenInstanceError):
            before.files[0].size_bytes = 10

    def test_invalid_records_do_not_mutate_state(self):
        """Verify the scenario: invalid records do not mutate state.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(self.service.snapshot().version, 0)
        """
        for args in [("", 1), ("a", -1), ("a", 1, {" "}), ("a\x7f", 1)]:
            with self.assertRaises(ValueError):
                FileRecord(*args)
        for args in [("a", True), ("a", 1.5), ("a", 1, "collection")]:
            with self.assertRaises(TypeError):
                FileRecord(*args)
        self.assertEqual(self.service.snapshot().version, 0)

    def test_random_mutations_match_recomputed_oracle(self):
        """Verify the scenario: random mutations match recomputed oracle.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assert_consistent(self.service.snapshot())
        """
        rng = random.Random(73)
        for _ in range(500):
            file_id = str(rng.randrange(20))
            if rng.randrange(4) == 0:
                self.service.delete(file_id)
            else:
                self.service.upsert(
                    FileRecord(file_id, rng.randrange(100), {str(rng.randrange(5))})
                )
            self.assert_consistent(self.service.snapshot())

    def test_concurrent_writers_and_snapshot_readers(self):
        """Verify the scenario: concurrent writers and snapshot readers.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assert_consistent(snapshot)
        """
        start = Barrier(6)

        def writer(worker):
            """Insert and selectively delete files while snapshot readers run.

            Called by: the enclosing test or its thread-pool callback.
            Returns: None; assertions raise on failure.
            Example (with test-local values): start.wait()
            """
            start.wait()
            for i in range(100):
                self.service.upsert(FileRecord(f"{worker}/{i}", i, {"all", str(worker)}))
                if i % 3 == 0:
                    self.service.delete(f"{worker}/{i}")

        def reader():
            """Repeatedly validate snapshots while other workers mutate files.

            Called by: the enclosing test or its thread-pool callback.
            Returns: None; assertions raise on failure.
            Example (with test-local values): start.wait()
            """
            start.wait()
            for _ in range(150):
                self.assert_consistent(self.service.snapshot())

        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(writer, i) for i in range(4)]
            futures += [executor.submit(reader) for _ in range(2)]
            for future in futures:
                future.result(timeout=20)
        snapshot = self.service.snapshot()
        self.assert_consistent(snapshot)
        self.assertEqual(len(snapshot.files), 4 * 66)

    def test_concurrent_compare_and_swap_has_single_winner(self):
        """Verify the scenario: concurrent compare and swap has single winner.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(sum(results), 1)
        """
        start = Barrier(8)

        def contender(i):
            """Race a version-zero file write and report whether it won.

            Called by: the enclosing test or its thread-pool callback.
            Returns: True; otherwise False.
            Example (with test-local values): start.wait()
            """
            start.wait()
            try:
                self.service.upsert(FileRecord(str(i), 1), expected_version=0)
                return True
            except VersionConflict:
                return False

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(contender, range(8)))
        self.assertEqual(sum(results), 1)
        self.assertEqual(self.service.snapshot().version, 1)


if __name__ == "__main__":
    unittest.main()
