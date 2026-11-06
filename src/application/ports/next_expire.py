from datetime import datetime
from typing import Awaitable, Callable

NextExpireAt = Callable[[], Awaitable[datetime | None]]
