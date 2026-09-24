"""Run a reproducible short game: python demo_ladder.py."""

import logging

from snake_ladder import Board, Game


class DemoDice:
    """A repeatable die for the console demonstration."""

    def roll(self) -> int:
        """Always roll two; the configured ladder leads straight to the win."""
        return 2


def main() -> None:
    """Keep presentation/logging outside the engine's critical section."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    game = Game(Board(10, {2: 10}), ["alice", "bob"], DemoDice())
    move = game.play_turn("alice", expected_version=0)
    logging.info(
        "player=%s roll=%s from=%s to=%s version=%s winner=%s",
        move.player_id,
        move.roll,
        move.before,
        move.after,
        move.state.version,
        move.state.winner,
    )


if __name__ == "__main__":
    main()
