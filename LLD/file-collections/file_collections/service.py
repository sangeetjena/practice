"""A single-process, linearizable in-memory collection accounting service."""

from dataclasses import dataclass
from heapq import nsmallest
from threading import RLock


class CapacityExceeded(Exception):
    """The operation exceeds the configured in-memory storage budget."""


class VersionConflict(Exception):
    """The caller's expected service version is stale."""


@dataclass(frozen=True, slots=True)
class FileRecord:
    file_id: str
    size_bytes: int
    collection_ids: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        _identifier(self.file_id)
        if isinstance(self.size_bytes, bool) or not isinstance(self.size_bytes, int):
            raise TypeError("size_bytes must be an integer")
        if self.size_bytes < 0:
            raise ValueError("size_bytes must not be negative")
        if isinstance(self.collection_ids, str):
            raise TypeError("collection_ids must be an iterable of identifiers")
        memberships = set()
        for index, collection_id in enumerate(self.collection_ids):
            if index >= 1000:
                raise ValueError("at most 1000 membership entries are accepted")
            _identifier(collection_id)
            memberships.add(collection_id)
        object.__setattr__(self, "collection_ids", frozenset(memberships))


def _identifier(value: str) -> None:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 128
        or any(ord(char) < 32 or ord(char) == 127 for char in value)
    ):
        raise ValueError("identifiers must be nonblank, trimmed strings of at most 128 characters")


@dataclass(frozen=True, slots=True)
class CollectionTotal:
    collection_id: str
    size_bytes: int
    file_count: int


@dataclass(frozen=True, slots=True)
class Snapshot:
    version: int
    total_size_bytes: int
    files: tuple[FileRecord, ...]
    collections: tuple[CollectionTotal, ...]


class FileCollections:
    """Atomic mutations; immutable, point-in-time reads.

    Equal upserts and missing deletes are no-ops. Every effective mutation
    increments the global version once. Identifiers are case-sensitive.
    """

    def __init__(self, *, max_files: int = 100_000, max_memberships: int = 1_000_000) -> None:
        if type(max_files) is not int or max_files < 1:
            raise ValueError("max_files must be a positive integer")
        if type(max_memberships) is not int or max_memberships < 1:
            raise ValueError("max_memberships must be a positive integer")
        self._max_files = max_files
        self._max_memberships = max_memberships
        self._membership_count = 0
        self._files: dict[str, FileRecord] = {}
        self._collection_sizes: dict[str, int] = {}
        self._collection_counts: dict[str, int] = {}
        self._total_size_bytes = 0
        self._version = 0
        self._lock = RLock()

    def upsert(self, file: FileRecord, *, expected_version: int | None = None) -> int:
        """Create or fully replace a file, including its complete memberships."""
        if not isinstance(file, FileRecord):
            raise TypeError("file must be a FileRecord")
        with self._lock:
            self._check_version(expected_version)
            previous = self._files.get(file.file_id)
            if previous == file:
                return self._version
            if previous is None and len(self._files) >= self._max_files:
                raise CapacityExceeded("file capacity exceeded")
            new_count = (
                self._membership_count
                + len(file.collection_ids)
                - (len(previous.collection_ids) if previous else 0)
            )
            if new_count > self._max_memberships:
                raise CapacityExceeded("membership capacity exceeded")
            if previous is not None:
                self._adjust(previous, -1)
            self._files[file.file_id] = file
            self._adjust(file, 1)
            self._membership_count = new_count
            self._version += 1
            return self._version

    def delete(self, file_id: str, *, expected_version: int | None = None) -> bool:
        """Remove a file and all contributions; return whether it existed."""
        _identifier(file_id)
        with self._lock:
            self._check_version(expected_version)
            previous = self._files.pop(file_id, None)
            if previous is None:
                return False
            self._adjust(previous, -1)
            self._membership_count -= len(previous.collection_ids)
            self._version += 1
            return True

    def _check_version(self, expected_version: int | None) -> None:
        if expected_version is not None:
            if isinstance(expected_version, bool) or not isinstance(expected_version, int):
                raise TypeError("expected_version must be an integer")
            if expected_version < 0:
                raise ValueError("expected_version must not be negative")
            if expected_version != self._version:
                raise VersionConflict(f"expected {expected_version}, current {self._version}")

    def _adjust(self, file: FileRecord, sign: int) -> None:
        self._total_size_bytes += sign * file.size_bytes
        for collection_id in file.collection_ids:
            count = self._collection_counts.get(collection_id, 0) + sign
            if count == 0:
                del self._collection_counts[collection_id]
                del self._collection_sizes[collection_id]
            else:
                self._collection_counts[collection_id] = count
                self._collection_sizes[collection_id] = (
                    self._collection_sizes.get(collection_id, 0) + sign * file.size_bytes
                )

    def snapshot(self) -> Snapshot:
        """Capture one consistent state; sort detached immutable values off-lock."""
        with self._lock:
            version = self._version
            total = self._total_size_bytes
            files = tuple(self._files.values())
            collections = self._collection_totals()
        return Snapshot(
            version,
            total,
            tuple(sorted(files, key=lambda file: file.file_id)),
            tuple(sorted(collections, key=lambda item: item.collection_id)),
        )

    def _collection_totals(self) -> tuple[CollectionTotal, ...]:
        return tuple(
            CollectionTotal(collection_id, size, self._collection_counts[collection_id])
            for collection_id, size in self._collection_sizes.items()
        )

    def top_k(self, k: int) -> tuple[CollectionTotal, ...]:
        """Rank by descending size, then ascending case-sensitive collection ID."""
        if isinstance(k, bool) or not isinstance(k, int):
            raise TypeError("k must be an integer")
        if k < 0:
            raise ValueError("k must not be negative")
        if k == 0:
            return ()
        with self._lock:
            collections = self._collection_totals()
        return tuple(
            nsmallest(k, collections, key=lambda item: (-item.size_bytes, item.collection_id))
        )
