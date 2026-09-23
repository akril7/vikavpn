from enum import StrEnum

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from database.crud import (
    MessengerAlreadyBoundError,
    bind_messenger,
    get_user_by_uuid,
)
from database.models import Messenger, User
from services.link import parse_uuid_from_link


class AuthResult(StrEnum):
    OK = "ok"
    USER_NOT_FOUND = "user_not_found"
    ALREADY_BOUND = "already_bound"


async def authorize_by_uuid(
    session: AsyncSession,
    messenger: Messenger,
    external_id: int,
    raw_uuid: str,
) -> tuple[AuthResult, User | None]:
    try:
        uuid = UUID(hex=raw_uuid)
    except (ValueError, AttributeError):
        logger.info(f"{messenger}:{external_id} — invalid uuid payload: {raw_uuid!r}")
        return AuthResult.USER_NOT_FOUND, None

    user = await get_user_by_uuid(session, uuid)
    if user is None:
        logger.info(f"{messenger}:{external_id} — user not found by uuid {uuid}")
        return AuthResult.USER_NOT_FOUND, None

    try:
        await bind_messenger(session, user, messenger, external_id)
    except MessengerAlreadyBoundError as e:
        logger.warning(str(e))
        return AuthResult.ALREADY_BOUND, None

    return AuthResult.OK, user


async def authorize_by_link(
    session: AsyncSession,
    messenger: Messenger,
    external_id: int,
    text: str,
) -> tuple[AuthResult, User | None]:
    uuid = parse_uuid_from_link(text)
    return await authorize_by_uuid(session, messenger, external_id, str(uuid))
