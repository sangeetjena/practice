from snake import Direction, SnakeGame


def main():
    """Run the snake-game demonstration using local objects.

    Called by: the script entry point.
    Returns: None; prints sample operation results.
    Example: python demo.py from the project directory.
    """
    game = SnakeGame(10, 10)
    for direction in [Direction.RIGHT] * 4 + [Direction.DOWN]:
        print(game.move(direction))
    print(game.snapshot())


if __name__ == "__main__":
    main()
