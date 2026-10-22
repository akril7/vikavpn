from enum import StrEnum

from loguru import logger
from uuid import UUID

from src.db.enums import Messenger
from src.db.models import User
from src.db.repo import UserMessengerRepository, UserRepository
from src.db.repo.messager import MessengerAlreadyBoundError
from src.core.url_build.link import parse_uuid_from_link


class AuthResult(StrEnum):
    OK = "ok"
    USER_NOT_FOUND = "user_not_found"
    ALREADY_BOUND = "already_bound"


async def authorize_by_uuid(
    user_repo: UserRepository,
    bind_repo: UserMessengerRepository,
    messenger: Messenger,
    external_id: int,
    raw_uuid: str,
) -> tuple[AuthResult, User | None]:
    try:
        uuid = UUID(hex=raw_uuid)
    except (ValueError, AttributeError, TypeError):
        logger.info(f"{messenger}:{external_id} — invalid uuid payload: {raw_uuid!r}")
        return AuthResult.USER_NOT_FOUND, None

    user = await user_repo.get_by_uuid(uuid)
    if user is None:
        logger.info(f"{messenger}:{external_id} — user not found by uuid {uuid}")
        return AuthResult.USER_NOT_FOUND, None

    try:
        await bind_repo.bind(
            user_id=user.id,
            messenger=messenger,
            external_id=external_id
        )
    except MessengerAlreadyBoundError as e:
        logger.warning(str(e))
        return AuthResult.ALREADY_BOUND, None

    return AuthResult.OK, user


async def authorize_by_link(
    user_repo: UserRepository,
    bind_repo: UserMessengerRepository,
    messenger: Messenger,
    external_id: int,
    text: str,
) -> tuple[AuthResult, User | None]:
    uuid = parse_uuid_from_link(text)
    return await authorize_by_uuid(user_repo, bind_repo, messenger, external_id, str(uuid))
