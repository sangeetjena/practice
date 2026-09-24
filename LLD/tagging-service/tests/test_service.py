"""Six compact tests to rehearse alongside the engine, using only unittest."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from tagging_service import Conflict, NotFound, ResourceKey, TaggingService


class TaggingTests(unittest.TestCase):
    def setUp(self):
        """Give every test independent state."""
        self.service = TaggingService("acme")
        self.issue = ResourceKey("jira", "issue", "123")
        self.tag = self.service.create_tag(" Backend ")

    def test_name_validation_and_get_or_create(self):
        """Normalization prevents duplicate tags, including compatibility text."""
        self.assertEqual(self.tag, self.service.create_tag("BACKEND"))
        self.assertEqual(self.tag, self.service.create_tag("Ｂａｃｋｅｎｄ"))  # noqa: RUF001
        for name in ("", "  ", None, "x" * 129):
            with self.assertRaises(ValueError):
                self.service.create_tag(name)
        with self.assertRaises(ValueError):
            ResourceKey("jira", "issue", "")

    def test_attach_detach_and_both_indexes(self):
        """Retries are no-ops and identical IDs in different products stay distinct."""
        page = ResourceKey("confluence", "page", "123")
        for resource in (self.issue, self.issue, page):
            self.service.attach_tag(resource, self.tag.tag_id)
        self.assertEqual(self.service.get_resource_tags(self.issue), {self.tag.tag_id})
        self.assertEqual(self.service.list_resources(self.tag.tag_id), {self.issue, page})
        old = self.service.get_resource_tags(self.issue)
        self.assertIsInstance(old, frozenset)
        for _ in range(2):
            self.service.detach_tag(self.issue, self.tag.tag_id)
        self.assertEqual(self.service.get_resource_tags(self.issue), set())
        self.assertEqual(self.service.list_resources(self.tag.tag_id), {page})
        self.assertEqual(old, {self.tag.tag_id})

    def test_rename_preserves_identity_and_rejects_conflict(self):
        """Renaming keeps assignments; a failed rename changes neither name."""
        self.service.attach_tag(self.issue, self.tag.tag_id)
        renamed = self.service.rename_tag(self.tag.tag_id, "API")
        self.assertEqual(renamed.tag_id, self.tag.tag_id)
        self.assertEqual(self.service.create_tag("api"), renamed)
        other = self.service.create_tag("Other")
        with self.assertRaises(Conflict):
            self.service.rename_tag(self.tag.tag_id, "other")
        self.assertEqual(self.service.get_tag(self.tag.tag_id), renamed)
        self.assertEqual(self.service.create_tag("other"), other)
        self.assertEqual(self.service.list_resources(renamed.tag_id), {self.issue})

    def test_delete_and_missing_tag(self):
        """Used tags cannot be deleted; unknown assignments never appear."""
        self.service.attach_tag(self.issue, self.tag.tag_id)
        with self.assertRaises(Conflict):
            self.service.delete_tag(self.tag.tag_id)
        self.service.detach_tag(self.issue, self.tag.tag_id)
        self.service.delete_tag(self.tag.tag_id)
        with self.assertRaises(NotFound):
            self.service.attach_tag(self.issue, self.tag.tag_id)
        with self.assertRaises(NotFound):
            self.service.get_tag(self.tag.tag_id)
        self.assertEqual(self.service.get_resource_tags(self.issue), set())
        self.assertNotEqual(self.service.create_tag("backend").tag_id, self.tag.tag_id)

    def test_tenant_instances_do_not_share_state(self):
        """Each tenant uses its own long-lived service instance."""
        other = TaggingService("other")
        with self.assertRaises(NotFound):
            other.attach_tag(self.issue, self.tag.tag_id)
        self.assertEqual(other.get_resource_tags(self.issue), set())

    def test_concurrent_create_and_attach(self):
        """Competing requests create one tag and preserve every reverse association."""
        barrier = Barrier(4)

        def attach(index):
            """Start contenders together, without sleep-based synchronization."""
            barrier.wait(timeout=5)
            tag = self.service.create_tag("release")
            resource = ResourceKey("jira", "issue", str(index))
            self.service.attach_tag(resource, tag.tag_id)
            return tag.tag_id, resource

        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(attach, range(4)))
        self.assertEqual(len({tag_id for tag_id, _ in results}), 1)
        tag_id = results[0][0]
        self.assertEqual(self.service.list_resources(tag_id), {r for _, r in results})
        for _, resource in results:
            self.assertEqual(self.service.get_resource_tags(resource), {tag_id})


if __name__ == "__main__":
    unittest.main()
