import secrets
import string
import uuid
from datetime import timedelta

from loguru import logger

from src.domain.enums import Messenger
from src.domain.models import User
from src.domain.utils.dt import utcnow
from src.application.ports.repo import UserMessengerRepoLike, UserRepoLike

WORDS_DICT = ("opos", "goga", "amer", "hehe", "afgn",
              "russ", "indi", "hool", "pool", "barb",
              "meme", "seqn", "bobr")

TRIAL_DAYS = 7
PASSWORD_ALPHABET = string.ascii_letters + string.digits
PASSWORD_LENGTH = 8


def generate_password() -> str:
    return "".join(secrets.choice(PASSWORD_ALPHABET) for _ in range(PASSWORD_LENGTH))


def generate_uuid() -> uuid.UUID:
    return uuid.uuid4()


def generate_name(uid: uuid.UUID) -> str:
    return f"{secrets.choice(WORDS_DICT)}_{uid.hex[:8]}"


async def register_user(
    user_repo: UserRepoLike,
    messenger_repo: UserMessengerRepoLike,
    ios_user: bool,
    messenger: tuple[Messenger, int] | None = None,
) -> User:
    """Создать нового пользователя с trial-подпиской и привязать к мессенджеру.

    Имя. uuid и пароль генерируются случайно.

    Запись добавляется в сессию через ``flush``, но **не коммитится** —
    коммит выполняет вызывающий код.

    Raises:
        IntegrityError: Сгенерированное имя или UUID оказалось неуникальным.
        MessengerAlreadyBoundError: ``external_id`` уже привязан
            к другому пользователю.
    """
    uid = generate_uuid()
    name = generate_name(uid)
    password = generate_password()

    user = await user_repo.create(
        name=name,
        password=password,
        uuid=uid,
        sub_expires_at=utcnow() + timedelta(days=TRIAL_DAYS),
        vpn_user=True,
        proxy_user=True,
        ios_user=ios_user,
    )

    if messenger:
        await messenger_repo.bind(
            user_id=user.id,
            messenger=messenger[0],
            external_id=messenger[1]
        )

    logger.info(f"Registered user {user.name} for {messenger[0]}:{messenger[1]}")

    return user
