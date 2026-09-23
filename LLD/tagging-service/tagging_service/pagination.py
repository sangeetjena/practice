"""Bounded, query-scoped cursors. Encoding is not authentication."""

import base64
import binascii
import json

from .models import ValidationError, identifier


def page_size(value: int) -> int:
    """Enforce integer page sizes from 1 through 100, excluding booleans.

    Called by: Paginated service methods before querying.
    Returns: Validated int; otherwise ValidationError.
    Example: page_size(50) returns 50; page_size(True) raises.
    """
    if type(value) is not int or not 1 <= value <= 100:
        raise ValidationError("page size must be an integer from 1 to 100")
    return value


def encode_cursor(scope: list[str], after: list[str]) -> str:
    """Encode format version, query scope and last sort key as URL-safe Base64.

    Called by: Service methods when an extra fetched row proves another page exists.
    Returns: Cursor string; encoding is not encryption or a signature.
    Example: encode_cursor(["tenant-a", "tags"], ["tag-2"]) bookmarks tag-2.
    """
    raw = json.dumps({"v": 1, "scope": scope, "after": after}, separators=(",", ":"))
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode_cursor(cursor: str | None, scope: list[str], width: int) -> list[str] | None:
    """Decode and validate a bounded cursor against this query and key width.

    Called by: Paginated service methods before building SQL seek conditions.
    Returns: List of last-key strings, or None for the first page; invalid input raises.
    Example: decode_cursor(None, ["tenant-a", "tags"], 1) returns None.
    """
    if cursor is None:
        return None
    try:
        if not isinstance(cursor, str) or not 0 < len(cursor) <= 8192:
            raise ValueError()
        data = json.loads(base64.b64decode(cursor, altchars=b"-_", validate=True))
        if (
            not isinstance(data, dict)
            or type(data.get("v")) is not int
            or data.get("v") != 1
            or data.get("scope") != scope
        ):
            raise ValueError()
        after = data["after"]
        if not isinstance(after, list) or len(after) != width:
            raise ValueError()
        if any(not isinstance(x, str) or not 0 < len(x) <= 128 for x in after):
            raise ValueError()
        for value in after:
            identifier(value, "cursor key")
        return after
    except (ValueError, TypeError, KeyError, UnicodeError, binascii.Error, RecursionError) as error:
        raise ValidationError("invalid cursor or cursor belongs to another query") from error
