"""Small, thread-safe Snake and Ladder engine; no HTTP or database dependencies."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from random import randint
from threading import Lock
from types import MappingProxyType
from typing import Protocol


class GameError(Exception):
    """Base for errors a caller can handle without inspecting message text."""


class InvalidInput(GameError, ValueError):
    """Configuration or a supplied value violates the game contract."""


class Conflict(GameError):
    """A stale version, wrong player or finished game prevents a turn."""


class Dice(Protocol):
    """A fast, trusted dice source; inject a separate instance for each game."""

    def roll(self) -> int:
        """Return an integer from 1 through 6, or raise before state changes."""
        ...


class RandomDice:
    """Default six-sided die; tests substitute a deterministic implementation."""

    def roll(self) -> int:
        """Choose one value from the six equally likely faces."""
        return randint(1, 6)


@dataclass(frozen=True)
class Board:
    """Immutable configuration with precomputed, cycle-free jump destinations.

    A source below its destination is a ladder, otherwise a snake. Cell zero
    is the starting area. Jumps cannot start at zero or the finishing cell.
    Construction is O(J); resolution is O(1), for J jump sources.
    """

    size: int = 100
    jumps: Mapping[int, int] = field(default_factory=dict, repr=False)
    _destinations: Mapping[int, int] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Copy and validate jumps, reject cycles, and memoize terminal cells."""
        if type(self.size) is not int or self.size < 2:
            raise InvalidInput("Board size must be an integer >= 2")
        jumps = dict(self.jumps)
        for start, end in jumps.items():
            if (
                type(start) is not int
                or type(end) is not int
                or not 1 <= start < self.size
                or not 1 <= end <= self.size
                or start == end
            ):
                raise InvalidInput("Invalid jump endpoints")
        resolved: dict[int, int] = {}
        for start in jumps:
            path: set[int] = set()
            cell = start
            while cell in jumps and cell not in resolved:
                if cell in path:
                    raise InvalidInput("Jump cycle detected")
                path.add(cell)
                cell = jumps[cell]
            destination = resolved.get(cell, cell)
            resolved.update((source, destination) for source in path)
        object.__setattr__(self, "jumps", MappingProxyType(jumps))
        object.__setattr__(self, "_destinations", MappingProxyType(resolved))

    def resolve(self, cell: int) -> int:
        """Resolve a valid landing cell through all jumps in constant time."""
        if type(cell) is not int or not 0 <= cell <= self.size:
            raise InvalidInput("Cell is outside the board")
        return self._destinations.get(cell, cell)


@dataclass(frozen=True)
class Snapshot:
    """Detached game view; tuples and scalar fields prevent external mutation."""

    positions: tuple[tuple[str, int], ...]
    next_player: str | None
    winner: str | None
    version: int


@dataclass(frozen=True)
class Move:
    """Successful turn; landed is the die target, even when it overshoots."""

    player_id: str
    roll: int
    before: int
    landed: int
    after: int
    state: Snapshot


class Game:
    """Own one roster and its mutable state; serialize operations with one lock.

    Starts immediately with 2-6 distinct nonempty player IDs. Position zero is
    off-board. Overshoots consume a turn; six grants no extra turn. A snapshot
    costs O(P); board resolution and state mutation cost O(1). State is volatile.
    """

    def __init__(self, board: Board, players: Sequence[str], dice: Dice | None = None):
        """Copy the roster, inject dice and initialize all players at zero."""
        roster = tuple(players)
        if (
            isinstance(players, (str, bytes))
            or not 2 <= len(roster) <= 6
            or any(not isinstance(p, str) or not p.strip() for p in roster)
            or len(set(roster)) != len(roster)
        ):
            raise InvalidInput("Provide 2-6 distinct nonempty player IDs")
        self._board = board
        self._dice = dice if dice is not None else RandomDice()
        self._players = roster
        self._positions = dict.fromkeys(roster, 0)
        self._turn = 0
        self._winner: str | None = None
        self._version = 0
        self._lock = Lock()

    def _snapshot(self) -> Snapshot:
        """Build a value copy; caller must already hold this game's lock."""
        return Snapshot(
            tuple(self._positions.items()),
            None if self._winner else self._players[self._turn],
            self._winner,
            self._version,
        )

    def snapshot(self) -> Snapshot:
        """Return a consistent immutable snapshot under the same lock as writes."""
        with self._lock:
            return self._snapshot()

    def play_turn(self, player_id: str, expected_version: int | None = None) -> Move:
        """Validate, roll, resolve and commit one complete turn atomically.

        Invalid input raises InvalidInput; stale/wrong/finished requests raise
        Conflict before consuming dice. Dice errors leave game state unchanged.
        Versions reject stale requests but do not replay prior responses. There
        is no durable idempotency, external authentication or distributed lock.
        """
        with self._lock:
            if expected_version is not None:
                if type(expected_version) is not int or expected_version < 0:
                    raise InvalidInput("Version must be a nonnegative integer")
                if expected_version != self._version:
                    raise Conflict("Stale version")
            if self._winner is not None:
                raise Conflict("Game is finished")
            if player_id != self._players[self._turn]:
                raise Conflict("Not this player's turn")
            roll = self._dice.roll()
            if type(roll) is not int or not 1 <= roll <= 6:
                raise InvalidInput("Dice must return an integer from 1 to 6")
            before = self._positions[player_id]
            landed = before + roll
            after = before if landed > self._board.size else self._board.resolve(landed)
            self._positions[player_id] = after
            if after == self._board.size:
                self._winner = player_id
            else:
                self._turn = (self._turn + 1) % len(self._players)
            self._version += 1
            return Move(player_id, roll, before, landed, after, self._snapshot())
