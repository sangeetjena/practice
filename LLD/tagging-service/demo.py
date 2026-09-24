"""Run the in-memory example: python demo.py."""

from tagging_service import ResourceKey, TaggingService


def main():
    """Create one reusable tenant service and tag two different products."""
    service = TaggingService("acme")
    release = service.create_tag("Release")
    issue = ResourceKey("jira", "issue", "123")
    page = ResourceKey("confluence", "page", "123")
    service.attach_tag(issue, release.tag_id)
    service.attach_tag(page, release.tag_id)
    print("Resource tags:", service.get_resource_tags(issue))
    print("Tagged resources:", service.list_resources(release.tag_id))
    print("Renamed:", service.rename_tag(release.tag_id, "Release candidate"))


if __name__ == "__main__":
    main()
