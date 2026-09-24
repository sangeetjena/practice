"""Behavioral tests for rules, immutable views and concurrent commands."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from threading import Barrier

from snake_ladder import Board, Conflict, Game, InvalidInput


class FixedDice:
    """Inject a known roll sequence and track whether rejected turns consume it."""

    def __init__(self, *rolls):
        """Store a deterministic iterator and call count."""
        self.rolls = iter(rolls)
        self.calls = 0

    def roll(self):
        """Return the next value; exhaustion intentionally raises StopIteration."""
        self.calls += 1
        return next(self.rolls)


class SnakeLadderTests(unittest.TestCase):
    """Exercise public behavior rather than private state layout."""

    def test_initial_state_and_copied_roster(self):
        """Caller-owned input changes cannot change game membership."""
        players = ["a", "b"]
        game = Game(Board(), players)
        players.append("c")
        self.assertEqual(game.snapshot().positions, (("a", 0), ("b", 0)))
        self.assertEqual(game.snapshot().next_player, "a")
        self.assertEqual(game.snapshot().version, 0)

    def test_chain_and_snake(self):
        """Resolve a ladder followed by a snake and a direct snake landing."""
        game = Game(Board(20, {2: 8, 8: 5, 6: 1}), ["a", "b"], FixedDice(2, 6))
        self.assertEqual(game.play_turn("a").after, 5)
        self.assertEqual(game.play_turn("b").after, 1)

    def test_overshoot_consumes_turn(self):
        """Overshooting leaves position unchanged but advances player/version."""
        game = Game(Board(5), ["a", "b"], FixedDice(4, 1, 2))
        game.play_turn("a")
        game.play_turn("b")
        move = game.play_turn("a")
        self.assertEqual((move.before, move.landed, move.after), (4, 6, 4))
        self.assertEqual((move.state.next_player, move.state.version), ("b", 3))

    def test_six_has_no_extra_turn_and_shared_cell_allowed(self):
        """Two players can occupy the same square; six follows normal rotation."""
        game = Game(Board(), ["a", "b"], FixedDice(6, 6))
        self.assertEqual(game.play_turn("a").state.next_player, "b")
        self.assertEqual(game.play_turn("b").state.positions, (("a", 6), ("b", 6)))

    def test_exact_win_and_terminal_rejection(self):
        """A winner ends the game without consuming further dice."""
        die = FixedDice(3)
        game = Game(Board(3), ["a", "b"], die)
        move = game.play_turn("a")
        self.assertEqual(move.state.winner, "a")
        self.assertIsNone(move.state.next_player)
        with self.assertRaises(Conflict):
            game.play_turn("b")
        self.assertEqual(die.calls, 1)

    def test_ladder_can_win(self):
        """Finishing through a jump is a valid win."""
        game = Game(Board(10, {2: 10}), ["a", "b"], FixedDice(2))
        self.assertEqual(game.play_turn("a").state.winner, "a")

    def test_wrong_player_and_stale_version_do_not_roll(self):
        """Rejected commands leave both state and the dice sequence untouched."""
        die = FixedDice(1)
        game = Game(Board(), ["a", "b"], die)
        for player, version in [("b", 0), ("a", 2), ("unknown", 0)]:
            with self.subTest(player=player, version=version), self.assertRaises(Conflict):
                game.play_turn(player, version)
        self.assertEqual(die.calls, 0)
        self.assertEqual(game.play_turn("a", 0).state.version, 1)
        with self.assertRaises(Conflict):
            game.play_turn("a", 0)

    def test_bad_roll_or_dice_failure_preserves_state(self):
        """Invalid dice values and a failed source cannot partially apply a turn."""
        for roll in [0, 7, True, 2.5, "2"]:
            game = Game(Board(), ["a", "b"], FixedDice(roll))
            before = game.snapshot()
            with self.subTest(roll=roll), self.assertRaises(InvalidInput):
                game.play_turn("a")
            self.assertEqual(game.snapshot(), before)
        game = Game(Board(), ["a", "b"], FixedDice())
        before = game.snapshot()
        with self.assertRaises(StopIteration):
            game.play_turn("a")
        self.assertEqual(game.snapshot(), before)

    def test_bad_boards(self):
        """Reject invalid sizes, endpoints, self jumps and multi-edge cycles."""
        for size, jumps in [
            (1, {}),
            (True, {}),
            (10, {0: 3}),
            (10, {10: 2}),
            (10, {2: 11}),
            (10, {2: 2}),
            (10, {2: 8, 8: 2}),
            (10, {2: 3, 3: 4, 4: 2}),
            (10, {2: 0}),
        ]:
            with self.subTest(size=size, jumps=jumps), self.assertRaises(InvalidInput):
                Board(size, jumps)

    def test_board_and_snapshot_are_immutable(self):
        """Defensive copying plus read-only nested data protects frozen values."""
        jumps = {2: 8}
        board = Board(10, jumps)
        jumps[2] = 4
        self.assertEqual(board.resolve(2), 8)
        with self.assertRaises(TypeError):
            board.jumps[2] = 4
        with self.assertRaises(FrozenInstanceError):
            board.size = 9
        game = Game(board, ["a", "b"], FixedDice(2))
        old = game.snapshot()
        game.play_turn("a")
        self.assertEqual(old.positions, (("a", 0), ("b", 0)))
        with self.assertRaises(FrozenInstanceError):
            old.version = 100

    def test_invalid_players_versions_and_cells(self):
        """Reject malformed public API inputs, including bool-as-int values."""
        for players in [[], ["a"], ["a", "a"], ["a", " "], ["a", []], "ab", list("abcdefg")]:
            with self.subTest(players=players), self.assertRaises(InvalidInput):
                Game(Board(), players)
        game = Game(Board(), ["a", "b"])
        for version in [-1, True, "0"]:
            with self.assertRaises(InvalidInput):
                game.play_turn("a", version)
        for cell in [-1, 101, True]:
            with self.assertRaises(InvalidInput):
                Board().resolve(cell)

    def test_long_chain_without_recursion(self):
        """Long valid chains are memoized without relying on Python recursion."""
        board = Board(3000, {i: i + 1 for i in range(1, 2999)})
        self.assertEqual(board.resolve(1), 2999)
        self.assertEqual(board.resolve(1500), 2999)

    def test_concurrent_same_version_has_one_winner(self):
        """Simultaneous commands apply once, with a coherent resulting snapshot."""
        die = FixedDice(1, 1)
        game = Game(Board(), ["a", "b"], die)
        barrier = Barrier(2)

        def attempt():
            """Start both contenders together without timing-dependent sleeps."""
            barrier.wait(timeout=3)
            try:
                return game.play_turn("a", 0)
            except Conflict:
                return None

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: attempt(), range(2)))
        self.assertEqual(sum(result is not None for result in results), 1)
        self.assertEqual(game.snapshot().version, 1)
        self.assertEqual(game.snapshot().positions, (("a", 1), ("b", 0)))
        self.assertEqual(die.calls, 1)

    def test_games_are_independent(self):
        """Sharing an immutable board does not share game positions or versions."""
        board = Board()
        first = Game(board, ["a", "b"], FixedDice(1))
        second = Game(board, ["a", "b"], FixedDice(2))
        first.play_turn("a")
        self.assertEqual(second.snapshot().version, 0)
        self.assertEqual(second.play_turn("a").after, 2)


if __name__ == "__main__":
    unittest.main()
