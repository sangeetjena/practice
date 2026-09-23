from file_collections import FileCollections, FileRecord


def main() -> None:
    """Run the file-collections demonstration using local objects.

    Called by: the script entry point.
    Returns: None; prints sample operation results.
    Example: python demo.py from the project directory.
    """
    service = FileCollections()
    service.upsert(FileRecord("design.pdf", 100, frozenset({"engineering", "release"})))
    service.upsert(FileRecord("notes.txt", 50, frozenset({"engineering"})))
    service.upsert(FileRecord("private.txt", 25))
    print("Unique storage:", service.snapshot().total_size_bytes)
    print("Top collections:", service.top_k(2))
    before = service.snapshot()
    service.upsert(
        FileRecord("notes.txt", 70, frozenset({"release"})), expected_version=before.version
    )
    print("After moving/resizing notes:", service.snapshot())
    print("Earlier snapshot still reports:", before.total_size_bytes)


if __name__ == "__main__":
    main()
