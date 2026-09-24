"""Run a short alternating Snake and Ladder game."""

from snake_ladder import Board, Game, InvalidInput


class DemoDice:
    """Return a predictable sequence so the turn flow is easy to follow."""

    def __init__(self) -> None:
        self._rolls = iter((2, 4, 6, 3, 5, 2, 4, 6))

    def roll(self) -> int:
        return next(self._rolls)


def main() -> None:
    """Play several turns, showing turn ownership and board movement."""
    game = Game(Board(30, {2: 10, 14: 6, 18: 25}), ["alice", "bob"], DemoDice())
    while not game.get_result().completed:
        state = game.get_current_state()
        player = state.next_player
        try:
            move = game.play_turn(player, expected_version=state.version)
        except (InvalidInput, StopIteration):
            break
        print(f"{move.player_id}: rolled {move.roll}, {move.before} -> {move.after}")
        print(f"  next player: {move.state.next_player or move.state.winner}")


if __name__ == "__main__":
    main()
