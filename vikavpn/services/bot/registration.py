import secrets
import string
from datetime import timedelta

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from database.enums import Messenger
from database.models import User
from database.repo.messager import UserMessengerRepository
from database.repo.user import UserRepository
from services.core.reload import schedule_reload
from utils.datetime import utcnow

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


async def generate_name(repo: UserRepository) -> str:
    for _ in range(20):
        candidate = _generate_candidate()
        if await repo.get_by_name(candidate) is None:
            return candidate

    raise RuntimeError("Cannot generate unique username")


async def register_user(
    session: AsyncSession,
    messenger: Messenger,
    external_id: int,
    ios_user: bool
) -> User:
    repo = UserRepository(session)

    name = await generate_name(repo)
    password = generate_password()

    user = await repo.create(
        name=name,
        password=password,
        sub_expires_at=utcnow() + timedelta(days=TRIAL_DAYS),
        vpn_user=True,
        proxy_user=True,
        ios_user=ios_user,
    )

    messenger_repo = UserMessengerRepository(session)
    await messenger_repo.bind(
        user_id=user.id,
        messenger=messenger,
        external_id=external_id
    )

    logger.info(f"Registered user {user.name} for {messenger}:{external_id}")
    schedule_reload()

    return user
