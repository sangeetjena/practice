from snake import Direction, SnakeGame


def main():
    game = SnakeGame(10, 10)
    for direction in [Direction.RIGHT] * 4 + [Direction.DOWN]:
        print(game.move(direction))
    print(game.snapshot())


if __name__ == "__main__":
    main()
