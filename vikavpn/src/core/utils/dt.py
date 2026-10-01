from datetime import datetime, UTC

from src.settings.app import TZ


def utcnow() -> datetime:
    return datetime.now(UTC)


def as_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=TZ)
    return dt


def format_date(dt: datetime) -> str:
    return as_aware(dt).strftime("%d.%m.%Y")
