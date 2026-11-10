from uuid import UUID

from src.infrastructure.persistence.repo import options


def parse_until(text: str):
    from datetime import UTC, datetime
    for fmt in ("%d.%m.%Y %H:%M", "%d.%m.%Y", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=UTC)
        except ValueError:
            continue
    return None


async def find_user(repo, name_or_uuid: str):
    user = await repo.get_by_name(name_or_uuid, options=options.full_options(),)
    if user is not None:
        return user
    try:
        uuid = UUID(hex=name_or_uuid)
    except (ValueError, TypeError):
        return None
    return await repo.get_by_uuid(uuid, options=options.full_options())
