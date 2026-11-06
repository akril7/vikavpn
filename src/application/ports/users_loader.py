from typing import Callable, Awaitable

from src.domain.models import User

UsersLoader = Callable[[], Awaitable[list[User]]]

