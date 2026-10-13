import secrets
import string
import uuid
from datetime import timedelta

from loguru import logger

from src.db.enums import Messenger
from src.db.models import User
from src.db.repo import UserMessengerRepository, UserRepository
from src.core.utils.dt import utcnow

WORDS_DICT = ("opos", "goga", "amer", "hehe", "afgn",
              "russ", "indi", "hool", "pool", "barb",
              "meme", "seqn", "bobr")

TRIAL_DAYS = 7
PASSWORD_ALPHABET = string.ascii_letters + string.digits
PASSWORD_LENGTH = 8


def generate_password() -> str:
    return "".join(secrets.choice(PASSWORD_ALPHABET) for _ in range(PASSWORD_LENGTH))


async def register_user(
    user_repo: UserRepository,
    messenger_repo: UserMessengerRepository,
    messenger: Messenger,
    external_id: int,
    ios_user: bool
) -> User:
    """Создать нового пользователя с trial-подпиской и привязать к мессенджеру.

    Генерирует уникальное имя и пароль, создаёт запись ``User``
    с trial-подпиской на TRIAL_DAYS дней, затем привязывает
    пользователя к указанному мессенджеру.

    Запись добавляется в сессию через ``flush``, но **не коммитится** —
    коммит выполняет вызывающий код.

    Args:
        user_repo: Репозиторий для создания пользователя.
        messenger_repo: Репозиторий для привязки к мессенджеру.
        messenger: Тип мессенджера (например, ``Messenger.TELEGRAM``).
        external_id: ID пользователя в мессенджере (например, Telegram ID).
        ios_user: Флаг, что пользователь на iOS (влияет на формат конфига).

    Returns:
        Созданный пользователь с заполненными ``id``, ``name``, ``password``,
        ``uuid`` и trial-подпиской.

    Raises:
        IntegrityError: Сгенерированное имя оказалось неуникальным.
        MessengerAlreadyBoundError: ``external_id`` уже привязан
            к другому пользователю.
    """
    uid = uuid.uuid4()
    name = f"{secrets.choice(WORDS_DICT)}_{uid.hex[:8]}"
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

    await messenger_repo.bind(
        user_id=user.id,
        messenger=messenger,
        external_id=external_id
    )

    logger.info(f"Registered user {user.name} for {messenger}:{external_id}")

    return user
