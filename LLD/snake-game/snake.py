"""Thread-safe game engine, independent of rendering, networking, and input devices."""

from collections import deque
from dataclasses import dataclass
from enum import Enum
from threading import Lock


class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


class Boundary(Enum):
    WALL = "wall"
    WRAP = "wrap"


class VersionConflict(Exception):
    """The command was based on an obsolete game snapshot."""


@dataclass(frozen=True)
class Cell:
    row: int
    column: int

    def __post_init__(self) -> None:
        """Reject non-integer coordinates after dataclass construction.

        Called by: Generated Cell constructor.
        Returns: None; invalid coordinates raise ValueError.
        Example: Cell(0, 2) is valid; Cell(True, 2) raises.
        """
        if type(self.row) is not int or type(self.column) is not int:
            raise ValueError("cell coordinates must be integers")


@dataclass(frozen=True)
class Snapshot:
    body: tuple[Cell, ...]  # Head first.
    direction: Direction
    successful_moves: int
    game_over: bool
    version: int


@dataclass(frozen=True)
class MoveResult:
    head: Cell
    length: int
    successful_moves: int
    game_over: bool
    version: int
    collision: str | None


class SnakeGame:
    """Initial body is (0,2),(0,1),(0,0), facing right. Growth is periodic.

    Each accepted move or terminal collision increments version. Invalid direction,
    forbidden reversal, and stale commands do not mutate state. Commands after game
    over are no-ops (unless their explicit expected version is stale).
    """

    def __init__(
        self, width: int, height: int, *, grow_every: int = 5, boundary: Boundary = Boundary.WALL
    ) -> None:
        """Validate board settings and initialize a three-cell snake facing right.

        Called by: Game setup or demo.
        Returns: None; construction produces a SnakeGame.
        Example: SnakeGame(10, 5) starts with head Cell(0, 2).
        """
        if type(width) is not int or width < 3 or type(height) is not int or height < 1:
            raise ValueError("width must be >= 3 and height >= 1, both integers")
        if type(grow_every) is not int or grow_every < 1:
            raise ValueError("grow_every must be a positive integer")
        if not isinstance(boundary, Boundary):
            raise ValueError("boundary must be a Boundary")
        self._width, self._height = width, height
        self._grow_every, self._boundary = grow_every, boundary
        self._body = deque([Cell(0, 2), Cell(0, 1), Cell(0, 0)])
        self._occupied = set(self._body)
        self._direction = Direction.RIGHT
        self._successful_moves = self._version = 0
        self._game_over = False
        self._collision = None
        self._lock = Lock()

    def snapshot(self) -> Snapshot:
        """Copy the complete game state under the lock.

        Called by: Renderer, client or tests.
        Returns: Immutable Snapshot with head-first body and version.
        Example: game.snapshot().version is 0 before any move.
        """
        with self._lock:
            return Snapshot(
                tuple(self._body),
                self._direction,
                self._successful_moves,
                self._game_over,
                self._version,
            )

    def _result(self) -> MoveResult:
        """Build a compact result from current fields; caller must hold the lock.

        Called by: move and _end_game.
        Returns: MoveResult, without mutating state.
        Example: After one right move on a wide board, head is Cell(0, 3).
        """
        return MoveResult(
            self._body[0],
            len(self._body),
            self._successful_moves,
            self._game_over,
            self._version,
            self._collision,
        )

    def move(self, direction: Direction, *, expected_version: int | None = None) -> MoveResult:
        """Validate a command and atomically move, grow or end the game.

        Called by: Input handler or demo.
        Returns: MoveResult; stale versions and reversals raise without mutation.
        Example: game.move(Direction.RIGHT, expected_version=0) performs the first move.
        """
        if not isinstance(direction, Direction):
            raise ValueError("direction must be a Direction")
        if expected_version is not None and (
            type(expected_version) is not int or expected_version < 0
        ):
            raise ValueError("expected_version must be a nonnegative integer")
        with self._lock:
            if expected_version is not None and expected_version != self._version:
                raise VersionConflict("game changed; read the current snapshot")
            if self._game_over:
                return self._result()
            row_delta, column_delta = direction.value
            old_row_delta, old_column_delta = self._direction.value
            if (row_delta, column_delta) == (-old_row_delta, -old_column_delta):
                raise ValueError("immediate reversal is not allowed")
            head = self._body[0]
            next_head = Cell(head.row + row_delta, head.column + column_delta)
            if self._boundary == Boundary.WRAP:
                next_head = Cell(next_head.row % self._height, next_head.column % self._width)
            elif not (0 <= next_head.row < self._height and 0 <= next_head.column < self._width):
                return self._end_game("wall")
            grows = (self._successful_moves + 1) % self._grow_every == 0
            # The current tail vacates on a non-growing move and is legal to enter.
            occupied = next_head in self._occupied
            tail_vacates = not grows and next_head == self._body[-1]
            if occupied and not tail_vacates:
                return self._end_game("self")
            if not grows:
                self._occupied.remove(self._body.pop())
            self._body.appendleft(next_head)
            self._occupied.add(next_head)
            self._direction = direction
            self._successful_moves += 1
            self._version += 1
            return self._result()

    def _end_game(self, collision: str) -> MoveResult:
        """Record a terminal collision and increment the version.

        Called by: move under the lock when a wall/body collision occurs.
        Returns: Terminal MoveResult.
        Example: _end_game("wall") records collision="wall" and game_over=True.
        """
        self._game_over = True
        self._collision = collision
        self._version += 1
        return self._result()
