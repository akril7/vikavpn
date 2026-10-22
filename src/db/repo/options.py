from sqlalchemy.orm import Load, selectinload

from src.db.models import User, UserManagement


Options = tuple[Load, ...]


def managed_options() -> Options:
    """User + managed_links + managed (двухуровневая загрузка)."""
    # noinspection PyTypeChecker
    return (
        selectinload(User.managed_links).joinedload(UserManagement.managed),
    )


def messenger_options() -> Options:
    """User + messenger_links."""
    # noinspection PyTypeChecker
    return (selectinload(User.messenger_links),)


def payments_options() -> Options:
    """User + payments."""
    # noinspection PyTypeChecker
    return (selectinload(User.payments),)


def manager_options() -> Options:
    """User + manager_links + manager (обратная сторона managed_links)."""
    # noinspection PyTypeChecker
    return (
        selectinload(User.manager_links).joinedload(UserManagement.manager),
    )
