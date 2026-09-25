"""Four essential interview tests; no database fixtures or timing sleeps."""

import unittest
from concurrent.futures import ThreadPoolExecutor

from tagging_service import Conflict, NotFound, ResourceKey, TaggingService


class TaggingTests(unittest.TestCase):
    def setUp(self):
        self.service = TaggingService("acme")
        self.issue = ResourceKey("jira", "issue", "1")
        self.tag = self.service.create_tag(" Backend ")

    def test_catalog(self):
        self.assertEqual(self.tag, self.service.create_tag("BACKEND"))
        with self.assertRaises(ValueError):
            self.service.create_tag(" ")
        renamed = self.service.rename_tag(self.tag.tag_id, "API")
        self.assertEqual(renamed.tag_id, self.tag.tag_id)
        other = self.service.create_tag("Other")
        with self.assertRaises(Conflict):
            self.service.rename_tag(renamed.tag_id, other.display_name)
        self.assertEqual(self.service.get_tag(renamed.tag_id), renamed)
        self.service.delete_tag(renamed.tag_id)
        with self.assertRaises(NotFound):
            self.service.get_tag(renamed.tag_id)

    def test_assignments_and_snapshot(self):
        for _ in range(2):
            self.service.attach_tag(self.issue, self.tag.tag_id)
        old = self.service.list_resources(self.tag.tag_id)
        self.assertEqual(old, {self.issue})
        self.assertEqual(self.service.get_resource_tags(self.issue), {self.tag.tag_id})
        with self.assertRaises(Conflict):
            self.service.delete_tag(self.tag.tag_id)
        for _ in range(2):
            self.service.detach_tag(self.issue, self.tag.tag_id)
        self.assertEqual(self.service.get_resource_tags(self.issue), frozenset())
        self.assertEqual(self.service.list_resources(self.tag.tag_id), frozenset())
        self.assertEqual(old, {self.issue})

    def test_top_k_and_tenant_isolation(self):
        other = self.service.create_tag("Other")
        page = ResourceKey("confluence", "page", "1")
        for tag, resource in [(self.tag, self.issue), (other, self.issue), (other, page)]:
            self.service.attach_tag(resource, tag.tag_id)
        self.assertEqual(self.service.top_k_tags(1), ((other, 2),))
        self.service.detach_tag(page, other.tag_id)
        expected = tuple(
            (t, 1) for t in sorted([self.tag, other], key=lambda t: t.tag_id, reverse=True)
        )
        self.assertEqual(self.service.top_k_tags(10), expected)
        self.assertEqual(self.service.top_k_tags(0), ())
        self.assertEqual(TaggingService("another-tenant").top_k_tags(10), ())
        for k in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                self.service.top_k_tags(k)

    def test_reads_do_not_wait_for_writer_lock(self):
        def read_all():
            return (
                self.service.get_tag(self.tag.tag_id),
                self.service.get_resource_tags(self.issue),
                self.service.list_resources(self.tag.tag_id),
                self.service.top_k_tags(1),
            )

        with ThreadPoolExecutor(max_workers=1) as pool:
            with self.service._lock:  # Another thread must finish reads while this is held.
                result = pool.submit(read_all).result(timeout=3)
        self.assertEqual(result, (self.tag, frozenset(), frozenset(), ()))


if __name__ == "__main__":
    unittest.main()
