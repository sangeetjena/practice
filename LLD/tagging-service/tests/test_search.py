import itertools

from test_service import ServiceFixture

from tagging_service import ResourceKey, TaggingService, ValidationError


class SearchTest(ServiceFixture):
    def setUp(self):
        """Prepare fresh state for each test so cases do not share mutations.

        Called by: unittest before each test case.
        Returns: None; assertions raise on failure.
        Example (with test-local values): super().setUp()
        """
        super().setUp()
        self.a = self.service.create_tag("backend")
        self.b = self.service.create_tag("release")
        self.both = ResourceKey("jira", "issue", "1")
        self.only_a = ResourceKey("confluence", "page", "2")
        self.only_b = ResourceKey("jira", "task", "3")
        for resource, tag in (
            (self.both, self.a),
            (self.both, self.b),
            (self.only_a, self.a),
            (self.only_b, self.b),
        ):
            self.service.attach_tag(resource, tag.tag_id)

    def test_all_any_and_missing_tags(self):
        """Verify the scenario: all any and missing tags.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual((self.both,), self.service.find_resources(ids).items)
        """
        ids = [self.a.tag_id, self.b.tag_id]
        self.assertEqual((self.both,), self.service.find_resources(ids).items)
        expected = tuple(sorted([self.both, self.only_a, self.only_b]))
        self.assertEqual(expected, self.service.find_resources(ids, match="any").items)
        self.assertEqual((), self.service.find_resources([self.a.tag_id, "missing"]).items)
        self.assertEqual(
            tuple(sorted([self.both, self.only_a])),
            self.service.find_resources([self.a.tag_id, "missing"], match="any").items,
        )

    def test_filters_and_tenant_isolation(self):
        """Verify the scenario: filters and tenant isolation.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual((self.only_b,), self.service.find_resources(ids, match='any', product='jira', resource_type='task').items)
        """
        ids = [self.a.tag_id, self.b.tag_id]
        self.assertEqual(
            (self.only_b,),
            self.service.find_resources(
                ids, match="any", product="jira", resource_type="task"
            ).items,
        )
        other = TaggingService(self.database, "tenant-b")
        self.assertEqual((), other.find_resources(ids, match="any").items)

    def test_pagination_and_query_binding(self):
        """Verify the scenario: pagination and query binding.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(tuple(sorted([self.both, self.only_a, self.only_b])), first.items + second.items)
        """
        ids = [self.a.tag_id, self.b.tag_id]
        first = self.service.find_resources(ids, match="any", limit=1)
        second = self.service.find_resources(
            list(reversed(ids)), match="any", limit=2, cursor=first.next_cursor
        )
        self.assertEqual(
            tuple(sorted([self.both, self.only_a, self.only_b])), first.items + second.items
        )
        self.assertIsNone(second.next_cursor)
        with self.assertRaises(ValidationError):
            self.service.find_resources(ids, match="all", cursor=first.next_cursor)
        with self.assertRaises(ValidationError):
            self.service.find_resources(ids, match="any", product="jira", cursor=first.next_cursor)

    def test_bounded_validation_and_duplicate_tags(self):
        """Verify the scenario: bounded validation and duplicate tags.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(self.service.find_resources([self.a.tag_id]), self.service.find_resources([self.a.tag_id, self.a.tag_id]))
        """
        for ids in ([], "tag", itertools.repeat(self.a.tag_id)):
            with self.assertRaises(ValidationError):
                self.service.find_resources(ids)
        with self.assertRaises(ValidationError):
            self.service.find_resources([self.a.tag_id], match="invalid")
        self.assertEqual(
            self.service.find_resources([self.a.tag_id]),
            self.service.find_resources([self.a.tag_id, self.a.tag_id]),
        )

    def test_prefix_is_normalized_literal_and_paginated(self):
        """Verify the scenario: prefix is normalized literal and paginated.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual((first_tag, second_tag), first.items + second.items)
        """
        first_tag = self.service.create_tag("Re%one")
        second_tag = self.service.create_tag("Re%two")
        self.service.create_tag("Re_other")
        first = self.service.search_tags(" RE% ", limit=1)
        second = self.service.search_tags("re%", limit=1, cursor=first.next_cursor)
        self.assertEqual((first_tag, second_tag), first.items + second.items)
        self.assertIsNone(second.next_cursor)
        with self.assertRaises(ValidationError):
            self.service.search_tags("other", cursor=first.next_cursor)
        self.assertEqual((), TaggingService(self.database, "tenant-b").search_tags("re").items)
        with self.assertRaises(ValidationError):
            self.service.search_tags("")
