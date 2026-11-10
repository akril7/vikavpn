from sqlalchemy.orm import Load, selectinload

from src.domain.models import User


Options = tuple[Load, ...]


def full_options() -> Options:
    return messenger_options() + payments_options()


def messenger_options() -> Options:
    """User + messenger_links."""
    # noinspection PyTypeChecker
    return (selectinload(User.messenger_links),)


def payments_options() -> Options:
    """User + payments."""
    # noinspection PyTypeChecker
    return (selectinload(User.payments),)
