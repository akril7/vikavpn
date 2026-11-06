from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy_utc import UtcDateTime

from src.domain.utils.dt import utcnow


class Base(DeclarativeBase):
    pass


class IdMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class CreateAtMixin:
    create_at: Mapped[datetime] = mapped_column(
        UtcDateTime,
        default=utcnow
    )
