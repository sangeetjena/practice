"""30-minute tagging exercise: one tenant, two indexes, one lock, no dependencies."""

from dataclasses import dataclass
from heapq import nlargest
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

    Writers serialize and publish a snapshot; reads take no application lock.
    Published dictionaries are never mutated and contain immutable values.
    This small CPython example permits reads of the previous published state.
    The caller supplies trusted tenant/resource identities; this is not
    an authentication layer or a multi-process database implementation.
    """

    def __init__(self, tenant_id: str):
        """Create an empty catalog and assignment indexes for one tenant."""
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("Tenant ID must be a nonempty string")
        self._tenant_id = tenant_id
        self._tags: dict[str, Tag] = {}
        self._names: dict[str, str] = {}
        self._resource_tags: dict[ResourceKey, frozenset[str]] = {}
        self._tag_resources: dict[str, frozenset[ResourceKey]] = {}
        self._lock = Lock()
        self._publish()

    def _publish(self):
        """Publish one coherent view; writers hold the lock except during init."""
        self._view = (self._tags.copy(), self._resource_tags.copy(), self._tag_resources.copy())

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
                self._tag_resources[tag.tag_id] = frozenset()
                self._publish()
            return self._tags[self._names[key]]

    def get_tag(self, tag_id: str) -> Tag:
        """Return immutable metadata, or raise NotFound."""
        tag = self._view[0].get(tag_id)
        if tag is None:
            raise NotFound(tag_id)
        return tag

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
            self._publish()
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
            self._publish()

    def attach_tag(self, resource: ResourceKey, tag_id: str) -> None:
        """Add an assignment idempotently and update both lookup directions."""
        with self._lock:
            self._tag(tag_id)
            self._resource_tags[resource] = self._resource_tags.get(resource, frozenset()) | {
                tag_id
            }
            self._tag_resources[tag_id] = self._tag_resources[tag_id] | {resource}
            self._publish()

    def detach_tag(self, resource: ResourceKey, tag_id: str) -> None:
        """Remove an assignment idempotently; unknown tag IDs raise NotFound."""
        with self._lock:
            self._tag(tag_id)
            tags = self._resource_tags.get(resource)
            if tags is not None:
                self._resource_tags[resource] = tags - {tag_id}
                if not self._resource_tags[resource]:
                    del self._resource_tags[resource]
            self._tag_resources[tag_id] = self._tag_resources[tag_id] - {resource}
            self._publish()

    def get_resource_tags(self, resource: ResourceKey) -> frozenset[str]:
        """Read published IDs without locking; an unseen resource has none."""
        return self._view[1].get(resource, frozenset())

    def list_resources(self, tag_id: str) -> frozenset[ResourceKey]:
        """Return resources for a known tag, without scanning all assignments."""
        resources = self._view[2].get(tag_id)
        if resources is None:
            raise NotFound(tag_id)
        return resources

    def top_k_tags(self, k: int) -> tuple[tuple[Tag, int], ...]:
        """Rank used tags by resource count, then tag ID descending, in one view."""
        if type(k) is not int or k < 0:
            raise ValueError("k must be a nonnegative integer")
        tags, _, resources = self._view
        ranked = nlargest(k, ((len(items), tag_id) for tag_id, items in resources.items() if items))
        return tuple((tags[tag_id], count) for count, tag_id in ranked)
