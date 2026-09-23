import secrets
import string
from datetime import datetime, timedelta, UTC

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

import core.commands
from database.crud import bind_messenger, create_user, get_user_by_name
from database.models import Messenger, User

ADJECTIVES = [
    "red", "fast", "lucky", "brave", "calm", "bright", "silent", "wild",
    "kind", "sharp", "swift", "bold", "wise", "free", "warm", "cool",
]

NOUNS = [
    "fox", "wolf", "cat", "hawk", "bear", "lion", "tiger", "eagle",
    "raven", "lynx", "panda", "otter", "falcon", "cobra", "moose", "orca",
]

TRIAL_DAYS = 5
PASSWORD_ALPHABET = string.ascii_letters + string.digits
PASSWORD_LENGTH = 8


def generate_password() -> str:
    return "".join(secrets.choice(PASSWORD_ALPHABET) for _ in range(PASSWORD_LENGTH))


def _generate_candidate() -> str:
    return f"{secrets.choice(ADJECTIVES)}_{secrets.choice(NOUNS)}_{secrets.randbelow(9999)}"


async def generate_name(session: AsyncSession) -> str:
    for _ in range(20):
        candidate = _generate_candidate()
        if await get_user_by_name(session, candidate) is None:
            return candidate

    raise RuntimeError("Cannot generate unique username")


async def register_user(
    session: AsyncSession,
    messenger: Messenger,
    external_id: int,
    ios_user: bool
) -> User:
    name = await generate_name(session)
    password = generate_password()

    user = await create_user(
        session=session,
        name=name,
        password=password,
        sub_expires_at=datetime.now(UTC) + timedelta(days=TRIAL_DAYS),
        vpn_user=True,
        proxy_user=True,
        ios_user=ios_user,
    )

    await bind_messenger(session, user, messenger, external_id)

    logger.info(f"Registered user {user.name} for {messenger}:{external_id}")
    await core.commands.reload_users()

    return user
