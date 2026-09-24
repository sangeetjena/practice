# Snake and Ladder

A compact, thread-safe Snake and Ladder engine for an LLD interview.

## Run

From this directory:

```powershell
python demo_ladder.py
python -m unittest discover -s tests -v
```

## Design

- `Position` describes a snake or ladder with `start` and `end` squares.
- `Board` owns immutable positions and resolves chained moves.
- `Member` identifies a player.
- `GameInterface` defines setup, state, result, and turn operations.
- `SnakeGame` implements the interface and protects state with one per-game lock.
- `Snapshot` reports every player's position and the next player's turn.
- `expected_version` rejects stale concurrent commands.

A wrong player receives `Conflict` immediately; the die is not rolled. The lock is
held only while validating and committing one turn, not while any external work runs.

The implementation intentionally keeps the interview contract small: board setup,
2-6 players, alternating turns, snakes/ladders, exact finish, snapshots, and
concurrency safety.
