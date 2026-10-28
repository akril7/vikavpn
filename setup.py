from src.settings import Settings
from src.infrastructure.manager.registry import Registry
from src.cli.actions.components import setup


def main():
    settings = Settings()
    registry = Registry(settings)

    if setup(registry):
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
