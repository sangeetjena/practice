import unittest
from threading import Barrier
from concurrent.futures import ThreadPoolExecutor

from snake_ladder import Board, Conflict, Game, InvalidInput, Position, PositionType


class Dice:
    def __init__(self, *rolls):
        self.rolls = iter(rolls)
        self.calls = 0

    def roll(self):
        self.calls += 1
        return next(self.rolls)


class SnakeLadderTests(unittest.TestCase):
    def test_position_resolution(self):
        board = Board(20, {
            2: Position(PositionType.LADDER, 2, 8),
            8: Position(PositionType.SNAKE, 8, 5),
        })
        self.assertEqual(board.resolve(2), 5)
        self.assertEqual(board.positions[2].type, PositionType.LADDER)

    def test_setup_and_turns(self):
        game = Game(Board(20, {2: 10}), ["alice", "bob"], Dice(2, 3))
        self.assertEqual(game.snapshot().next_player, "alice")
        self.assertEqual(game.play_turn("alice").after, 10)
        self.assertEqual(game.play_turn("bob").after, 3)

    def test_wrong_player_does_not_roll(self):
        dice = Dice(2)
        game = Game(Board(), ["alice", "bob"], dice)
        with self.assertRaisesRegex(Conflict, "alice"):
            game.play_turn("bob")
        self.assertEqual(dice.calls, 0)

    def test_lifecycle_validation(self):
        game = Game(dice=Dice(1))
        with self.assertRaises(Conflict):
            game.play_turn("alice")
        game.select_board(Board())
        game.choose_member("alice")
        with self.assertRaises(InvalidInput):
            game.start_game()
        game.choose_member("bob")
        game.start_game()
        with self.assertRaises(Conflict):
            game.start_game()

    def test_winner_and_finished_game(self):
        game = Game(Board(3), ["alice", "bob"], Dice(3, 1))
        move = game.play_turn("alice")
        self.assertEqual(game.get_result().winner, "alice")
        self.assertTrue(game.get_result().completed)
        with self.assertRaises(Conflict):
            game.play_turn("bob")
        self.assertEqual(move.state.next_player, None)

    def test_stale_version_does_not_roll(self):
        dice = Dice(1, 2)
        game = Game(Board(), ["alice", "bob"], dice)
        game.play_turn("alice", expected_version=0)
        with self.assertRaises(Conflict):
            game.play_turn("bob", expected_version=0)
        self.assertEqual(dice.calls, 1)

    def test_concurrent_same_turn_has_one_winner(self):
        game = Game(Board(), ["alice", "bob"], Dice(1, 1))
        barrier = Barrier(2)

        def attempt():
            barrier.wait()
            try:
                game.play_turn("alice", expected_version=0)
                return 1
            except Conflict:
                return 0

        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sum(pool.map(lambda _: attempt(), range(2))), 1)


if __name__ == "__main__":
    unittest.main()
