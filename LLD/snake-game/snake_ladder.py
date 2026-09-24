"""Small, thread-safe Snake and Ladder game."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from random import randint
from threading import Lock
from types import MappingProxyType
from typing import Protocol


class GameError(Exception):
    """Base class for expected game errors."""


class InvalidInput(GameError, ValueError):
    """A board, member, die, or command is invalid."""


class Conflict(GameError):
    """The game is not ready, the player is wrong, or the version is stale."""


class Dice(Protocol):
    def roll(self) -> int: ...


class RandomDice:
    def roll(self) -> int:
        return randint(1, 6)


class PositionType(Enum):
    SNAKE = "snake"
    LADDER = "ladder"


@dataclass(frozen=True)
class Position:
    type: PositionType
    start: int
    end: int

    @property
    def index(self) -> int:
        return self.start

    def __post_init__(self) -> None:
        if not isinstance(self.type, PositionType):
            raise InvalidInput("invalid position type")
        if type(self.start) is not int or type(self.end) is not int:
            raise InvalidInput("position endpoints must be integers")
        if self.start == self.end:
            raise InvalidInput("position endpoints must differ")
        if self.type is PositionType.LADDER and self.end < self.start:
            raise InvalidInput("ladder must move forward")
        if self.type is PositionType.SNAKE and self.end > self.start:
            raise InvalidInput("snake must move backward")


@dataclass(frozen=True)
class Member:
    member_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.member_id, str) or not self.member_id.strip():
            raise InvalidInput("member ID must be nonempty")


@dataclass(frozen=True)
class Board:
    size: int = 100
    positions: Mapping[int, Position | int] = field(default_factory=dict, repr=False)
    _destinations: Mapping[int, int] = field(init=False, repr=False, compare=False)
    _jumps: Mapping[int, int] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if type(self.size) is not int or self.size < 2:
            raise InvalidInput("board size must be at least 2")
        positions: dict[int, Position] = {}
        for start, value in dict(self.positions).items():
            if type(start) is not int:
                raise InvalidInput("position index must be an integer")
            if isinstance(value, Position):
                position = value
            elif type(value) is int:
                position = Position(
                    PositionType.LADDER if value > start else PositionType.SNAKE,
                    start,
                    value,
                )
            else:
                raise InvalidInput("invalid board position")
            if position.start != start or not 1 <= start < self.size or not 1 <= position.end <= self.size:
                raise InvalidInput("position is outside the board")
            positions[start] = position

        jumps = {start: position.end for start, position in positions.items()}
        destinations: dict[int, int] = {}
        for start in jumps:
            path: set[int] = set()
            cell = start
            while cell in jumps:
                if cell in path:
                    raise InvalidInput("position cycle detected")
                if cell in destinations:
                    cell = destinations[cell]
                    break
                path.add(cell)
                cell = jumps[cell]
            destinations.update({source: cell for source in path})
        object.__setattr__(self, "positions", MappingProxyType(positions))
        object.__setattr__(self, "_jumps", MappingProxyType(jumps))
        object.__setattr__(self, "_destinations", MappingProxyType(destinations))

    @property
    def jumps(self) -> Mapping[int, int]:
        return self._jumps

    def resolve(self, cell: int) -> int:
        if type(cell) is not int or not 0 <= cell <= self.size:
            raise InvalidInput("cell is outside the board")
        return self._destinations.get(cell, cell)


@dataclass(frozen=True)
class Snapshot:
    positions: tuple[tuple[str, int], ...]
    next_player: str | None
    winner: str | None
    version: int
    started: bool


@dataclass(frozen=True)
class Move:
    player_id: str
    roll: int
    before: int
    landed: int
    after: int
    state: Snapshot


@dataclass(frozen=True)
class GameResult:
    completed: bool
    winner: str | None
    state: Snapshot


class GameInterface(Protocol):
    def select_board(self, board: Board) -> None: ...
    def choose_member(self, member: Member | str) -> None: ...
    def start_game(self) -> None: ...
    def get_current_state(self) -> Snapshot: ...
    def get_result(self) -> GameResult: ...
    def play_turn(self, player_id: str, expected_version: int | None = None) -> Move: ...


class SnakeGame(GameInterface):
    def __init__(
        self,
        board: Board | None = None,
        players: Sequence[Member | str] | None = None,
        dice: Dice | None = None,
    ) -> None:
        self._board: Board | None = None
        self._dice = dice if dice is not None else RandomDice()
        self._players: tuple[Member, ...] = ()
        self._positions: dict[str, int] = {}
        self._turn = 0
        self._winner: str | None = None
        self._version = 0
        self._started = False
        self._lock = Lock()
        if board is not None:
            self.select_board(board)
        if players is not None:
            for player in players:
                self.choose_member(player)
        if board is not None and players is not None:
            self.start_game()

    def select_board(self, board: Board) -> None:
        if not isinstance(board, Board):
            raise InvalidInput("board must be a Board")
        with self._lock:
            if self._started:
                raise Conflict("game already started")
            self._board = board

    def choose_member(self, member: Member | str) -> None:
        selected = member if isinstance(member, Member) else Member(member)
        with self._lock:
            if self._started:
                raise Conflict("game already started")
            if len(self._players) == 6:
                raise InvalidInput("maximum six members")
            if selected.member_id in {item.member_id for item in self._players}:
                raise InvalidInput("member IDs must be unique")
            self._players += (selected,)

    def start_game(self) -> None:
        with self._lock:
            if self._started:
                raise Conflict("game already started")
            if self._board is None or not 2 <= len(self._players) <= 6:
                raise InvalidInput("select a board and 2-6 members first")
            self._positions = {player.member_id: 0 for player in self._players}
            self._started = True

    def _snapshot(self) -> Snapshot:
        next_player = None
        if self._started and self._winner is None:
            next_player = self._players[self._turn].member_id
        return Snapshot(tuple(self._positions.items()), next_player, self._winner, self._version, self._started)

    def get_current_state(self) -> Snapshot:
        with self._lock:
            return self._snapshot()

    def get_result(self) -> GameResult:
        with self._lock:
            return GameResult(self._winner is not None, self._winner, self._snapshot())

    def snapshot(self) -> Snapshot:
        return self.get_current_state()

    def play_turn(self, player_id: str, expected_version: int | None = None) -> Move:
        with self._lock:
            if expected_version is not None:
                if type(expected_version) is not int or expected_version < 0:
                    raise InvalidInput("expected version must be a nonnegative integer")
                if expected_version != self._version:
                    raise Conflict("stale version")
            if not self._started:
                raise Conflict("game has not started")
            if self._winner is not None:
                raise Conflict("game is finished")
            if player_id != self._players[self._turn].member_id:
                raise Conflict(f"it is {self._players[self._turn].member_id}'s turn")
            roll = self._dice.roll()
            if type(roll) is not int or not 1 <= roll <= 6:
                raise InvalidInput("dice must return an integer from 1 through 6")
            assert self._board is not None
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


Game = SnakeGame
