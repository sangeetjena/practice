"""Run with python demo.py. Uses an isolated temporary local database."""

from pathlib import Path
from tempfile import TemporaryDirectory

from tagging_service import Conflict, Database, ResourceKey, TaggingService


def main() -> None:
    with TemporaryDirectory(prefix="tagging-demo-") as directory:
        database = Database(Path(directory) / "demo.sqlite3")
        database.initialize()
        service = TaggingService(database, "acme")
        release = service.create_tag("Release 2026")
        backend = service.create_tag("Backend")
        issue = ResourceKey("jira", "issue", "123")
        page = ResourceKey("confluence", "page", "123")
        first = service.attach_tag(issue, release.tag_id)
        service.attach_tag(page, release.tag_id)
        print("Shared tag across products:", service.list_resources(release.tag_id))
        updated = service.replace_tags(
            issue, [release.tag_id, backend.tag_id], expected_version=first.version
        )
        print("Atomic replacement:", updated)
        try:
            service.replace_tags(issue, [], expected_version=first.version)
        except Conflict as error:
            print("Stale writer rejected:", error)
        print("Other tenant:", TaggingService(database, "other").get_resource_tags(issue))


if __name__ == "__main__":
    main()
