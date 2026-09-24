"""Small in-memory tagging service for a timed interview."""

from .service import Conflict, NotFound, ResourceKey, Tag, TaggingService

__all__ = ["Conflict", "NotFound", "ResourceKey", "Tag", "TaggingService"]
