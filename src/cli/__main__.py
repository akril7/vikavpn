from src.cli.app import run


def main() -> None:
    try:
        run()
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
