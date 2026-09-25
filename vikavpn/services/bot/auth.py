from enum import StrEnum

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from database.enums import Messenger
from database.models import User
from database.repo.messager import UserMessengerRepository, MessengerAlreadyBoundError
from database.repo.user import UserRepository
from services.url_build import parse_uuid_from_link


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

    user_repo = UserRepository(session)

    user = await user_repo.get_by_uuid(uuid)
    if user is None:
        logger.info(f"{messenger}:{external_id} — user not found by uuid {uuid}")
        return AuthResult.USER_NOT_FOUND, None

    bind_repo = UserMessengerRepository(session)
    try:
        await bind_repo.bind(
            user_id=user.id,
            messenger=messenger,
            external_id=external_id
        )
        await session.commit()
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
