"""Thread-safe, copy-on-write segment router; Python 3.11 standard library."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from threading import Lock
from types import MappingProxyType

Handler = Callable[..., object]
MAX_SEGMENTS = 128
MAX_PATH_LENGTH = 8192


class RouteConflictError(ValueError):
    """A registration duplicates a route or conflicts with a parameter name."""


def _method(value: str) -> str:
    if not isinstance(value, str) or not value or not value.isascii() or not value.isalpha():
        raise ValueError("method must contain ASCII letters")
    return value.upper()


def _segments(path: str, *, pattern: bool = False) -> tuple[str, ...]:
    if not isinstance(path, str) or not path.startswith("/"):
        raise ValueError("path must be an absolute path")
    if len(path) > MAX_PATH_LENGTH or any(c in path for c in "?#"):
        raise ValueError("path too long or contains query/fragment")
    if any(ord(c) < 32 or ord(c) == 127 or c == "\\" for c in path):
        raise ValueError("path contains control characters or backslashes")
    if path == "/":
        return ()
    parts = tuple(path.removesuffix("/")[1:].split("/"))
    if len(parts) > MAX_SEGMENTS or any(not part or part in {".", ".."} for part in parts):
        raise ValueError("empty/dot segments or too many segments")
    if pattern:
        names: set[str] = set()
        for part in parts:
            if part.startswith(":"):
                name = part[1:]
                if not name.isidentifier() or not name.isascii() or name in names:
                    raise ValueError("parameter names must be unique ASCII identifiers")
                names.add(name)
            elif "*" in part and part != "*":
                raise ValueError("wildcard must occupy exactly one segment")
    return parts


@dataclass(frozen=True)
class RouteMatch:
    handler: Handler
    parameters: Mapping[str, str]
    pattern: str
    method: str


@dataclass(frozen=True)
class _Node:
    literals: Mapping[str, _Node] = field(default_factory=lambda: MappingProxyType({}))
    parameter_name: str | None = None
    parameter: _Node | None = None
    wildcard: _Node | None = None
    handler: Handler | None = None
    pattern: str | None = None


def _insert(
    node: _Node, parts: tuple[str, ...], index: int, handler: Handler, pattern: str
) -> _Node:
    if index == len(parts):
        if node.handler is not None:
            raise RouteConflictError(f"route already registered: {pattern}")
        return _Node(
            node.literals, node.parameter_name, node.parameter, node.wildcard, handler, pattern
        )
    part = parts[index]
    literals, parameter_name, parameter, wildcard = (
        node.literals,
        node.parameter_name,
        node.parameter,
        node.wildcard,
    )
    if part.startswith(":"):
        name = part[1:]
        if parameter_name is not None and parameter_name != name:
            raise RouteConflictError(f"shared parameter edge is named {parameter_name}, not {name}")
        parameter_name = name
        parameter = _insert(parameter or _Node(), parts, index + 1, handler, pattern)
    elif part == "*":
        wildcard = _insert(wildcard or _Node(), parts, index + 1, handler, pattern)
    else:
        updated = dict(literals)
        updated[part] = _insert(updated.get(part, _Node()), parts, index + 1, handler, pattern)
        literals = MappingProxyType(updated)
    return _Node(literals, parameter_name, parameter, wildcard, node.handler, node.pattern)


class Router:
    """Snapshot lookups; literal > parameter > wildcard among complete matches.

    Registration is atomic. Existing matches and in-flight lookups retain their
    snapshot. Handlers run only when the caller explicitly invokes them.
    """

    def __init__(self) -> None:
        self._roots: dict[str, _Node] = {}
        self._lock = Lock()

    def register(self, pattern: str, handler: Handler, *, method: str = "GET") -> None:
        method = _method(method)
        parts = _segments(pattern, pattern=True)
        if not callable(handler):
            raise TypeError("handler must be callable")
        canonical_pattern = "/" + "/".join(parts)
        with self._lock:
            # Build before publishing: conflicts leave the old root untouched.
            new_root = _insert(
                self._roots.get(method, _Node()), parts, 0, handler, canonical_pattern
            )
            self._roots[method] = new_root

    def resolve(self, path: str, *, method: str = "GET") -> RouteMatch | None:
        method = _method(method)
        parts = _segments(path)
        with self._lock:
            root = self._roots.get(method)
        if root is None:
            return None

        def visit(node: _Node, index: int, parameters: dict[str, str]) -> RouteMatch | None:
            if index == len(parts):
                if node.handler is None:
                    return None
                return RouteMatch(
                    node.handler, MappingProxyType(dict(parameters)), node.pattern or "/", method
                )
            segment = parts[index]
            literal = node.literals.get(segment)
            if literal is not None:
                match = visit(literal, index + 1, parameters)
                if match is not None:
                    return match
            if node.parameter is not None:
                assert node.parameter_name is not None
                parameters[node.parameter_name] = segment
                match = visit(node.parameter, index + 1, parameters)
                del parameters[node.parameter_name]
                if match is not None:
                    return match
            if node.wildcard is not None:
                return visit(node.wildcard, index + 1, parameters)
            return None

        return visit(root, 0, {})
