import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from snake import Boundary, Cell, Direction, SnakeGame, VersionConflict


class SnakeTest(unittest.TestCase):
    def test_initial_and_growth(self):
        """Verify the scenario: initial and growth.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(Cell(0, 2), game.snapshot().body[0])
        """
        game = SnakeGame(20, 2)
        self.assertEqual(Cell(0, 2), game.snapshot().body[0])
        for _ in range(4):
            self.assertEqual(3, game.move(Direction.RIGHT).length)
        self.assertEqual(4, game.move(Direction.RIGHT).length)

    def test_wall_and_terminal_noop(self):
        """Verify the scenario: wall and terminal noop.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual('wall', result.collision)
        """
        game = SnakeGame(3, 2)
        before = game.snapshot()
        result = game.move(Direction.RIGHT)
        self.assertEqual("wall", result.collision)
        self.assertEqual(before.body, game.snapshot().body)
        self.assertEqual(result, game.move(Direction.DOWN))

    def test_tail_cell_legal_when_vacating(self):
        """Verify the scenario: tail cell legal when vacating.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertFalse(result.game_over)
        """
        game = SnakeGame(3, 1, boundary=Boundary.WRAP)
        result = game.move(Direction.RIGHT)
        self.assertFalse(result.game_over)
        self.assertEqual(Cell(0, 0), result.head)
        self.assertEqual(3, len(set(game.snapshot().body)))

    def test_tail_cell_collision_when_growing(self):
        """Verify the scenario: tail cell collision when growing.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual('self', game.move(Direction.RIGHT).collision)
        """
        game = SnakeGame(3, 1, boundary=Boundary.WRAP, grow_every=1)
        self.assertEqual("self", game.move(Direction.RIGHT).collision)

    def test_self_collision(self):
        """Verify the scenario: self collision.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual('self', result.collision)
        """
        game = SnakeGame(10, 10, grow_every=1)
        for direction in (Direction.DOWN, Direction.LEFT, Direction.UP):
            result = game.move(direction)
        self.assertEqual("self", result.collision)

    def test_invalid_input_preserves_state(self):
        """Verify the scenario: invalid input preserves state.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(original, game.snapshot())
        """
        game = SnakeGame(10, 10)
        original = game.snapshot()
        for direction in (Direction.LEFT, "RIGHT", None):
            with self.assertRaises(ValueError):
                game.move(direction)
            self.assertEqual(original, game.snapshot())
        with self.assertRaises(ValueError):
            game.move(Direction.RIGHT, expected_version=True)

    def test_configuration(self):
        """Verify the scenario: configuration.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertRaises(ValueError)
        """
        for args in ((2, 2), (True, 2), (3, 0)):
            with self.assertRaises(ValueError):
                SnakeGame(*args)
        with self.assertRaises(ValueError):
            SnakeGame(3, 3, grow_every=0)

    def test_stale_command(self):
        """Verify the scenario: stale command.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(1, game.snapshot().successful_moves)
        """
        game = SnakeGame(10, 10)
        game.move(Direction.RIGHT, expected_version=0)
        with self.assertRaises(VersionConflict):
            game.move(Direction.DOWN, expected_version=0)
        self.assertEqual(1, game.snapshot().successful_moves)

    def test_concurrent_commands_one_version_winner(self):
        """Verify the scenario: concurrent commands one version winner.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(1, sum(pool.map(command, range(8))))
        """
        game = SnakeGame(30, 2)
        barrier = Barrier(8)

        def command(_):
            """Race one snake command against the same expected version.

            Called by: the enclosing test or its thread-pool callback.
            Returns: 1; otherwise 0.
            Example (with test-local values): barrier.wait(timeout=5)
            """
            barrier.wait(timeout=5)
            try:
                game.move(Direction.RIGHT, expected_version=0)
                return 1
            except VersionConflict:
                return 0

        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(1, sum(pool.map(command, range(8))))

    def test_concurrent_moves_preserve_body(self):
        """Verify the scenario: concurrent moves preserve body.

        Called by: unittest discovery with the fixtures arranged below.
        Returns: None; failed expectations raise assertion errors.
        Example expectation (using the fixture below): self.assertEqual(200, state.successful_moves)
        """
        game = SnakeGame(1000, 2)
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(lambda _: game.move(Direction.RIGHT), range(200)))
        state = game.snapshot()
        self.assertEqual(200, state.successful_moves)
        self.assertEqual(43, len(state.body))
        self.assertEqual(len(state.body), len(set(state.body)))


if __name__ == "__main__":
    unittest.main()
