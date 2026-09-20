"""Immutable public contracts and domain errors; no database dependencies."""

import unicodedata
from dataclasses import dataclass
from typing import Generic, TypeVar


class TaggingError(Exception):
    """Base error for an expected domain failure."""


class ValidationError(TaggingError):
    """The caller supplied an invalid argument."""


class NotFound(TaggingError):
    """An entity does not exist in the selected tenant."""


class Conflict(TaggingError):
    """A uniqueness constraint or expected version was violated."""


def identifier(value: str, field: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 128:
        raise ValidationError(f"{field} must be a nonempty string of at most 128 characters")
    if value != value.strip() or any(unicodedata.category(c).startswith("C") for c in value):
        raise ValidationError(
            f"{field} must not contain surrounding whitespace or control characters"
        )
    return value


def tag_name(value: str) -> tuple[str, str]:
    if not isinstance(value, str):
        raise ValidationError("tag name must be a string")
    display = unicodedata.normalize("NFKC", value).strip()
    identifier(display, "tag name")
    normalized = display.casefold()
    if len(normalized) > 128:
        raise ValidationError("normalized tag name exceeds 128 characters")
    return display, normalized


@dataclass(frozen=True, order=True)
class ResourceKey:
    product: str
    resource_type: str
    resource_id: str

    def __post_init__(self) -> None:
        for field in ("product", "resource_type", "resource_id"):
            identifier(getattr(self, field), field)

    def values(self) -> tuple[str, str, str]:
        return self.product, self.resource_type, self.resource_id


@dataclass(frozen=True)
class Tag:
    tag_id: str
    display_name: str
    version: int


T = TypeVar("T")


@dataclass(frozen=True)
class Page(Generic[T]):
    items: tuple[T, ...]
    next_cursor: str | None


@dataclass(frozen=True)
class ResourceTags:
    tag_ids: tuple[str, ...]
    version: int
