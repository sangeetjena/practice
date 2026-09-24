"""30-minute tagging exercise: one tenant, two indexes, one lock, no dependencies."""

from dataclasses import dataclass
from threading import Lock
from unicodedata import normalize
from uuid import uuid4


class NotFound(KeyError):
    """The requested tag does not exist in this service instance."""


class Conflict(ValueError):
    """A name is taken or a tag is still assigned to resources."""


@dataclass(frozen=True)
class ResourceKey:
    """Product/type/ID avoids collisions between different products' resources."""

    product: str
    resource_type: str
    resource_id: str

    def __post_init__(self):
        """Reject empty or non-string identity components."""
        if any(
            not isinstance(v, str) or not v.strip()
            for v in (self.product, self.resource_type, self.resource_id)
        ):
            raise ValueError("Resource identifiers must be nonempty strings")


@dataclass(frozen=True)
class Tag:
    """An immutable tag view; renaming preserves tag_id."""

    tag_id: str
    display_name: str


def tag_name(name: str) -> str:
    """Validate and normalize display text; casefold is used for uniqueness."""
    if not isinstance(name, str):
        raise ValueError("Tag name must be a string")
    name = normalize("NFKC", name).strip()
    if not 1 <= len(name) <= 128:
        raise ValueError("Tag name must contain 1-128 characters")
    return name


class TaggingService:
    """Reuse one instance per tenant; all state is lost on process restart.

    Both assignment indexes change under the same lock. Reads return immutable
    copies. The caller supplies trusted tenant/resource identities; this is not
    an authentication layer or a multi-process database implementation.
    """

    def __init__(self, tenant_id: str):
        """Create an empty catalog and assignment indexes for one tenant."""
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("Tenant ID must be a nonempty string")
        self._tenant_id = tenant_id
        self._tags: dict[str, Tag] = {}
        self._names: dict[str, str] = {}
        self._resource_tags: dict[ResourceKey, set[str]] = {}
        self._tag_resources: dict[str, set[ResourceKey]] = {}
        self._lock = Lock()

    def _tag(self, tag_id: str) -> Tag:
        """Load a known tag; the caller must hold the lock."""
        if tag_id not in self._tags:
            raise NotFound(tag_id)
        return self._tags[tag_id]

    def create_tag(self, name: str) -> Tag:
        """Get or create by normalized name; the first display spelling wins."""
        display = tag_name(name)
        key = display.casefold()
        with self._lock:
            if key not in self._names:
                tag = Tag(uuid4().hex, display)
                self._tags[tag.tag_id] = tag
                self._names[key] = tag.tag_id
                self._tag_resources[tag.tag_id] = set()
            return self._tags[self._names[key]]

    def get_tag(self, tag_id: str) -> Tag:
        """Return immutable metadata, or raise NotFound."""
        with self._lock:
            return self._tag(tag_id)

    def rename_tag(self, tag_id: str, name: str) -> Tag:
        """Rename without changing assignments; a taken name raises Conflict."""
        display = tag_name(name)
        key = display.casefold()
        with self._lock:
            old = self._tag(tag_id)
            if key in self._names and self._names[key] != tag_id:
                raise Conflict("Tag name already exists")
            del self._names[old.display_name.casefold()]
            self._names[key] = tag_id
            self._tags[tag_id] = Tag(tag_id, display)
            return self._tags[tag_id]

    def delete_tag(self, tag_id: str) -> None:
        """Delete only unused tags; detach assignments first."""
        with self._lock:
            tag = self._tag(tag_id)
            if self._tag_resources[tag_id]:
                raise Conflict("Tag is still in use")
            del self._names[tag.display_name.casefold()]
            del self._tags[tag_id]
            del self._tag_resources[tag_id]

    def attach_tag(self, resource: ResourceKey, tag_id: str) -> None:
        """Add an assignment idempotently and update both lookup directions."""
        with self._lock:
            self._tag(tag_id)
            self._resource_tags.setdefault(resource, set()).add(tag_id)
            self._tag_resources[tag_id].add(resource)

    def detach_tag(self, resource: ResourceKey, tag_id: str) -> None:
        """Remove an assignment idempotently; unknown tag IDs raise NotFound."""
        with self._lock:
            self._tag(tag_id)
            tags = self._resource_tags.get(resource)
            if tags is not None:
                tags.discard(tag_id)
                if not tags:
                    del self._resource_tags[resource]
            self._tag_resources[tag_id].discard(resource)

    def get_resource_tags(self, resource: ResourceKey) -> frozenset[str]:
        """Return tag IDs as an immutable copy; an unseen resource has none."""
        with self._lock:
            return frozenset(self._resource_tags.get(resource, ()))

    def list_resources(self, tag_id: str) -> frozenset[ResourceKey]:
        """Return resources for a known tag, without scanning all assignments."""
        with self._lock:
            self._tag(tag_id)
            return frozenset(self._tag_resources[tag_id])
