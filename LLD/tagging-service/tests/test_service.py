import sqlite3
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from pathlib import Path

from tagging_service import (
    Conflict,
    Database,
    NotFound,
    ResourceKey,
    TaggingService,
    ValidationError,
)


class ServiceFixture(unittest.TestCase):
    def setUp(self):
        """Prepare fresh state for each test so cases do not share mutations.

        Called by: unittest before each test case.
        Returns: None; assertions raise on failure.
        Example (with test-local values): tempfile.TemporaryDirectory(prefix='tagging-test-')
        """
        self.directory = tempfile.TemporaryDirectory(prefix="tagging-test-")
        self.addCleanup(self.directory.cleanup)
        self.database = Database(Path(self.directory.name) / "test.sqlite3")
        self.database.initialize()
        self.service = TaggingService(self.database, "tenant-a")
        self.resource = ResourceKey("jira", "issue", "123")


class ServiceTest(ServiceFixture):
    def test_normalized_create_is_idempotent(self):
        """Verify the scenario: normalized create is idempotent.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(first, self.service.create_tag('BACKEND'))
        """
        first = self.service.create_tag(" Backend ")
        self.assertEqual(first, self.service.create_tag("BACKEND"))
        # Compatibility characters intentionally exercise NFKC normalization.
        self.assertEqual(first, self.service.create_tag("Ｂａｃｋｅｎｄ"))  # noqa: RUF001

    def test_invalid_names_and_identifiers(self):
        """Verify the scenario: invalid names and identifiers.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertRaises(ValidationError)
        """
        for name in ("", "  ", "a\x00b", "a" * 129, None):
            with self.subTest(name=name), self.assertRaises(ValidationError):
                self.service.create_tag(name)
        with self.assertRaises(ValidationError):
            ResourceKey("jira", "issue", " 123")

    def test_tenant_and_product_isolation(self):
        """Verify the scenario: tenant and product isolation.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual((), self.service.get_resource_tags(page).tag_ids)
        """
        tag = self.service.create_tag("release")
        self.service.attach_tag(self.resource, tag.tag_id)
        page = ResourceKey("confluence", "page", "123")
        self.assertEqual((), self.service.get_resource_tags(page).tag_ids)
        other = TaggingService(self.database, "tenant-b")
        self.assertEqual((), other.get_resource_tags(self.resource).tag_ids)
        with self.assertRaises(NotFound):
            other.attach_tag(self.resource, tag.tag_id)
        self.assertNotEqual(tag.tag_id, other.create_tag("release").tag_id)

    def test_idempotent_attach_and_detach_versions(self):
        """Verify the scenario: idempotent attach and detach versions.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(1, first.version)
        """
        tag = self.service.create_tag("release")
        first = self.service.attach_tag(self.resource, tag.tag_id)
        self.assertEqual(1, first.version)
        self.assertEqual(first, self.service.attach_tag(self.resource, tag.tag_id))
        removed = self.service.detach_tag(self.resource, tag.tag_id)
        self.assertEqual(2, removed.version)
        self.assertEqual((), removed.tag_ids)
        self.assertEqual(removed, self.service.detach_tag(self.resource, tag.tag_id))
        self.assertEqual((), self.service.list_resources(tag.tag_id).items)

    def test_rename_preserves_assignments_and_checks_version(self):
        """Verify the scenario: rename preserves assignments and checks version.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(tag.tag_id, renamed.tag_id)
        """
        tag = self.service.create_tag("release")
        self.service.attach_tag(self.resource, tag.tag_id)
        renamed = self.service.rename_tag(tag.tag_id, "launch", expected_version=0)
        self.assertEqual(tag.tag_id, renamed.tag_id)
        self.assertEqual(1, renamed.version)
        self.assertEqual((self.resource,), self.service.list_resources(tag.tag_id).items)
        with self.assertRaises(Conflict):
            self.service.rename_tag(tag.tag_id, "stale", expected_version=0)

    def test_duplicate_rename_rolls_back(self):
        """Verify the scenario: duplicate rename rolls back.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(first, self.service.get_tag(first.tag_id))
        """
        first = self.service.create_tag("one")
        self.service.create_tag("two")
        with self.assertRaises(Conflict):
            self.service.rename_tag(first.tag_id, "TWO", expected_version=0)
        self.assertEqual(first, self.service.get_tag(first.tag_id))

    def test_delete_restricts_used_tags(self):
        """Verify the scenario: delete restricts used tags.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertRaises(Conflict)
        """
        tag = self.service.create_tag("release")
        self.service.attach_tag(self.resource, tag.tag_id)
        with self.assertRaises(Conflict):
            self.service.delete_tag(tag.tag_id, expected_version=0)
        self.service.detach_tag(self.resource, tag.tag_id)
        self.service.delete_tag(tag.tag_id, expected_version=0)
        with self.assertRaises(NotFound):
            self.service.get_tag(tag.tag_id)

    def test_replace_validates_every_tag_before_mutating(self):
        """Verify the scenario: replace validates every tag before mutating.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(before, self.service.get_resource_tags(self.resource))
        """
        tag = self.service.create_tag("release")
        before = self.service.attach_tag(self.resource, tag.tag_id)
        with self.assertRaises(NotFound):
            self.service.replace_tags(self.resource, ["missing"], expected_version=before.version)
        self.assertEqual(before, self.service.get_resource_tags(self.resource))

    def test_replace_deduplicates_and_preserves_noop_version(self):
        """Verify the scenario: replace deduplicates and preserves noop version.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual((tag.tag_id,), result.tag_ids)
        """
        tag = self.service.create_tag("release")
        result = self.service.replace_tags(self.resource, [tag.tag_id] * 2, expected_version=0)
        self.assertEqual((tag.tag_id,), result.tag_ids)
        self.assertEqual(
            result,
            self.service.replace_tags(self.resource, [tag.tag_id], expected_version=1),
        )
        with self.assertRaises(Conflict):
            self.service.replace_tags(self.resource, [], expected_version=0)

    def test_replace_input_is_bounded_and_version_is_validated(self):
        """Verify the scenario: replace input is bounded and version is validated.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertRaises(ValidationError)
        """
        for ids in (["x"] * 1001, "a-tag-id", None):
            with self.subTest(ids=type(ids)), self.assertRaises(ValidationError):
                self.service.replace_tags(self.resource, ids, expected_version=0)
        for version in (-1, True, "0"):
            with self.subTest(version=version), self.assertRaises(ValidationError):
                self.service.replace_tags(self.resource, [], expected_version=version)

    def test_snapshot_is_immutable_and_persistent(self):
        """Verify the scenario: snapshot is immutable and persistent.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(snapshot, reopened.get_resource_tags(self.resource))
        """
        tag = self.service.create_tag("release")
        snapshot = self.service.attach_tag(self.resource, tag.tag_id)
        with self.assertRaises(FrozenInstanceError):
            snapshot.version = 999
        reopened = TaggingService(Database(self.database.path), "tenant-a")
        self.assertEqual(snapshot, reopened.get_resource_tags(self.resource))

    def test_resource_pagination_has_no_duplicates_on_stable_data(self):
        """Verify the scenario: resource pagination has no duplicates on stable data.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(expected, found)
        """
        tag = self.service.create_tag("release")
        expected = [ResourceKey("jira", "issue", str(i)) for i in range(7)]
        for resource in expected:
            self.service.attach_tag(resource, tag.tag_id)
        found, cursor = [], None
        while True:
            page = self.service.list_resources(tag.tag_id, limit=2, cursor=cursor)
            found.extend(page.items)
            cursor = page.next_cursor
            if cursor is None:
                break
        self.assertEqual(expected, found)

    def test_tag_pagination_and_cursor_scope(self):
        """Verify the scenario: tag pagination and cursor scope.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(sorted((t.tag_id for t in tags)), [t.tag_id for t in page.items + remainder.items])
        """
        tags = [self.service.create_tag(str(i)) for i in range(3)]
        page = self.service.list_tags(limit=2)
        remainder = self.service.list_tags(limit=2, cursor=page.next_cursor)
        self.assertEqual(
            sorted(t.tag_id for t in tags),
            [t.tag_id for t in page.items + remainder.items],
        )
        with self.assertRaises(ValidationError):
            TaggingService(self.database, "other").list_tags(cursor=page.next_cursor)
        with self.assertRaises(ValidationError):
            self.service.list_resources(tags[0].tag_id, cursor=page.next_cursor)

    def test_invalid_pagination(self):
        """Verify the scenario: invalid pagination.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertRaises(ValidationError)
        """
        for size in (0, -1, 101, True, "10"):
            with self.subTest(size=size), self.assertRaises(ValidationError):
                self.service.list_tags(limit=size)
        for cursor in ("bad!", "W10=", "", "x" * 8193):
            with self.subTest(cursor=cursor[:10]), self.assertRaises(ValidationError):
                self.service.list_tags(cursor=cursor)

    def test_transaction_rolls_back_after_partial_write(self):
        """Verify the scenario: transaction rolls back after partial write.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertRaises(RuntimeError)
        """
        with self.assertRaises(RuntimeError):
            with self.database.transaction(write=True) as connection:
                connection.execute("INSERT INTO tags VALUES ('tenant-a','x','x','x',0)")
                raise RuntimeError("injected failure")
        with self.assertRaises(NotFound):
            self.service.get_tag("x")

    def test_database_enforces_foreign_keys(self):
        """Verify the scenario: database enforces foreign keys.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertRaises(sqlite3.IntegrityError)
        """
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction(write=True) as connection:
                connection.execute("INSERT INTO assignments VALUES ('t','p','k','r','missing')")

    def test_exact_tag_limit_and_overflow(self):
        """Verify the scenario: exact tag limit and overflow.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(1000, len(full.tag_ids))
        """
        tag_ids = [f"tag-{i}" for i in range(1001)]
        with self.database.transaction(write=True) as connection:
            connection.executemany(
                "INSERT INTO tags VALUES ('tenant-a',?,?,?,0)",
                [(tag_id, tag_id, tag_id) for tag_id in tag_ids],
            )
        full = self.service.replace_tags(self.resource, tag_ids[:1000], expected_version=0)
        self.assertEqual(1000, len(full.tag_ids))
        self.assertEqual(full, self.service.attach_tag(self.resource, tag_ids[0]))
        with self.assertRaises(ValidationError):
            self.service.attach_tag(self.resource, tag_ids[-1])
        self.assertEqual(full, self.service.get_resource_tags(self.resource))

    def test_sql_syntax_in_name_is_stored_as_data(self):
        """Verify the scenario: sql syntax in name is stored as data.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(name, self.service.get_tag(tag.tag_id).display_name)
        """
        name = "release'; DROP TABLE tags; --"
        tag = self.service.create_tag(name)
        self.assertEqual(name, self.service.get_tag(tag.tag_id).display_name)
        self.assertEqual(1, len(self.service.list_tags().items))


class ConcurrentServiceTest(ServiceFixture):
    def run_concurrently(self, action, workers=8):
        """Start barrier-synchronized actions using separate tenant service instances.

        Called by: the enclosing test or its thread-pool callback.
        Returns: List of action results in worker-index order; worker exceptions propagate.
        Example (with test-local values): threading.Barrier(workers)
        """
        barrier = threading.Barrier(workers)

        def run(index):
            """Wait at the shared barrier and invoke the supplied action on a fresh service.

            Called by: the enclosing test or its thread-pool callback.
            Returns: action(service, index).
            Example (with test-local values): barrier.wait(timeout=10)
            """
            barrier.wait(timeout=10)
            # Different service AND Database objects prove no shared Python lock is required.
            service = TaggingService(Database(self.database.path), "tenant-a")
            return action(service, index)

        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(run, range(workers)))

    def test_concurrent_create_deduplicates(self):
        """Verify the scenario: concurrent create deduplicates.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(1, len({tag.tag_id for tag in results}))
        """
        results = self.run_concurrently(lambda service, _: service.create_tag("shared"))
        self.assertEqual(1, len({tag.tag_id for tag in results}))

    def test_concurrent_duplicate_attach_increments_once(self):
        """Verify the scenario: concurrent duplicate attach increments once.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertTrue(all((result.version == 1 for result in results)))
        """
        tag = self.service.create_tag("shared")
        results = self.run_concurrently(
            lambda service, _: service.attach_tag(self.resource, tag.tag_id)
        )
        self.assertTrue(all(result.version == 1 for result in results))

    def test_concurrent_distinct_attach_has_no_lost_updates(self):
        """Verify the scenario: concurrent distinct attach has no lost updates.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(8, result.version)
        """
        tags = [self.service.create_tag(str(i)) for i in range(8)]
        self.run_concurrently(lambda service, i: service.attach_tag(self.resource, tags[i].tag_id))
        result = self.service.get_resource_tags(self.resource)
        self.assertEqual(8, result.version)
        self.assertEqual({tag.tag_id for tag in tags}, set(result.tag_ids))

    def test_concurrent_replace_has_exactly_one_winner(self):
        """Verify the scenario: concurrent replace has exactly one winner.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(1, sum(self.run_concurrently(replace)))
        """
        tags = [self.service.create_tag(str(i)) for i in range(8)]

        def replace(service, index):
            """Attempt replacement at version zero and report whether this writer won.

            Called by: the enclosing test or its thread-pool callback.
            Returns: True; otherwise False.
            Example (with test-local values): service.replace_tags(self.resource, [tags[index].tag_id], expected_version=0)
            """
            try:
                service.replace_tags(self.resource, [tags[index].tag_id], expected_version=0)
                return True
            except Conflict:
                return False

        self.assertEqual(1, sum(self.run_concurrently(replace)))
        self.assertEqual(1, self.service.get_resource_tags(self.resource).version)

    def test_concurrent_duplicate_detach_increments_once(self):
        """Verify the scenario: concurrent duplicate detach increments once.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertTrue(all((result.version == 2 and (not result.tag_ids) for result in results)))
        """
        tag = self.service.create_tag("shared")
        self.service.attach_tag(self.resource, tag.tag_id)
        results = self.run_concurrently(
            lambda service, _: service.detach_tag(self.resource, tag.tag_id)
        )
        self.assertTrue(all(result.version == 2 and not result.tag_ids for result in results))

    def test_delete_racing_attach_preserves_referential_integrity(self):
        """Verify the scenario: delete racing attach preserves referential integrity.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(['rejected', 'success'], sorted(self.run_concurrently(mutate, workers=2)))
        """
        tag = self.service.create_tag("shared")

        def mutate(service, index):
            """Race deletion against attachment and classify domain conflicts.

            Called by: the enclosing test or its thread-pool callback.
            Returns: 'success'; otherwise 'rejected'.
            Example (with test-local values): service.delete_tag(tag.tag_id, expected_version=0)
            """
            try:
                if index == 0:
                    service.delete_tag(tag.tag_id, expected_version=0)
                else:
                    service.attach_tag(self.resource, tag.tag_id)
                return "success"
            except (Conflict, NotFound):
                return "rejected"

        self.assertEqual(["rejected", "success"], sorted(self.run_concurrently(mutate, workers=2)))
        with self.database.transaction() as connection:
            self.assertEqual([], connection.execute("PRAGMA foreign_key_check").fetchall())

    def test_readers_never_observe_partial_replacement(self):
        """Verify the scenario: readers never observe partial replacement.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertIn(set(service.get_resource_tags(self.resource).tag_ids), [left, right])
        """
        tags = [self.service.create_tag(str(i)).tag_id for i in range(8)]
        left, right = set(tags[:4]), set(tags[4:])
        self.service.replace_tags(self.resource, left, expected_version=0)

        def workload(service, index):
            """Alternate complete tag sets in one writer while other workers verify snapshots.

            Called by: the enclosing test or its thread-pool callback.
            Returns: None; assertions raise on failure.
            Example (with test-local values): service.get_resource_tags(self.resource)
            """
            if index == 0:
                for turn in range(30):
                    snapshot = service.get_resource_tags(self.resource)
                    service.replace_tags(
                        self.resource,
                        right if turn % 2 == 0 else left,
                        expected_version=snapshot.version,
                    )
            else:
                for _ in range(40):
                    self.assertIn(
                        set(service.get_resource_tags(self.resource).tag_ids),
                        [left, right],
                    )

        self.run_concurrently(workload, workers=4)

    def test_reader_sees_committed_snapshot_while_writer_is_open(self):
        """Verify the scenario: reader sees committed snapshot while writer is open.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(before, seen)
        """
        tag = self.service.create_tag("release")
        before = self.service.attach_tag(self.resource, tag.tag_id)
        with self.database.transaction(write=True) as connection:
            connection.execute("DELETE FROM assignments")
            with ThreadPoolExecutor(max_workers=1) as pool:
                seen = pool.submit(self.service.get_resource_tags, self.resource).result(timeout=5)
            self.assertEqual(before, seen)

    def test_lock_timeout_is_bounded_and_does_not_mutate(self):
        """Verify the scenario: lock timeout is bounded and does not mutate.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual((), self.service.list_tags().items)
        """
        service = TaggingService(
            Database(self.database.path, busy_timeout_seconds=0.05), "tenant-a"
        )
        with self.database.transaction(write=True):
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(service.create_tag, "blocked")
                with self.assertRaises(sqlite3.OperationalError):
                    future.result(timeout=5)
        self.assertEqual((), self.service.list_tags().items)


if __name__ == "__main__":
    unittest.main()
