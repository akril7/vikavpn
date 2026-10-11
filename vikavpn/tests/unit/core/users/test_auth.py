import uuid

from src.core.users.flow.auth import AuthResult, authorize_by_link, authorize_by_uuid
from src.db.enums import Messenger
from src.db.models import User
from src.db.repo import UserMessengerRepository, UserRepository


async def _create_user_with_messenger(
    session, *, external_id: int,
) -> "User":
    """Создаёт user и привязывает к нему messenger. Возвращает User."""
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    user = await user_repo.create(
        name=f"u_{uuid.uuid4().hex[:8]}",
        password="pwd",
        uuid=uuid.uuid4(),
    )
    await messenger_repo.bind(
        user_id=user.id,
        messenger=Messenger.TELEGRAM,
        external_id=external_id,
    )
    return user


# ----- authorize_by_uuid -----

async def test_authorize_by_uuid_success(session):
    user = await _create_user_with_messenger(session, external_id=10)
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    result, authorized = await authorize_by_uuid(
        user_repo, messenger_repo,
        Messenger.TELEGRAM, external_id=999, raw_uuid=user.uuid.hex,
    )

    assert result == AuthResult.OK
    assert authorized is not None
    assert authorized.id == user.id


async def test_authorize_by_uuid_invalid_format(session):
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    result, authorized = await authorize_by_uuid(
        user_repo, messenger_repo,
        Messenger.TELEGRAM, external_id=1, raw_uuid="not-a-uuid",
    )
    assert result == AuthResult.USER_NOT_FOUND
    assert authorized is None


async def test_authorize_by_uuid_empty_string(session):
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    result, authorized = await authorize_by_uuid(
        user_repo, messenger_repo,
        Messenger.TELEGRAM, external_id=1, raw_uuid="",
    )
    assert result == AuthResult.USER_NOT_FOUND
    assert authorized is None


async def test_authorize_by_uuid_user_not_found(session):
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    result, authorized = await authorize_by_uuid(
        user_repo, messenger_repo,
        Messenger.TELEGRAM, external_id=1, raw_uuid=uuid.uuid4().hex,
    )
    assert result == AuthResult.USER_NOT_FOUND
    assert authorized is None


async def test_authorize_by_uuid_same_user_idempotent(session):
    """Повторный bind того же (user, messenger, external_id) — OK."""
    user = await _create_user_with_messenger(session, external_id=100)
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    result, authorized = await authorize_by_uuid(
        user_repo, messenger_repo,
        Messenger.TELEGRAM, external_id=100, raw_uuid=user.uuid.hex,
    )

    assert result == AuthResult.OK
    assert authorized is not None
    assert authorized.id == user.id


async def test_authorize_by_uuid_conflict_with_other_user(session):
    """external_id занят другим user → ALREADY_BOUND."""
    u1 = await _create_user_with_messenger(session, external_id=100)
    u2 = await _create_user_with_messenger(session, external_id=200)
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    result, authorized = await authorize_by_uuid(
        user_repo, messenger_repo,
        Messenger.TELEGRAM, external_id=100, raw_uuid=u2.uuid.hex,
    )

    assert result == AuthResult.ALREADY_BOUND
    assert authorized is None


# ----- authorize_by_link -----

async def test_authorize_by_link_tg_proxy(session):
    user = await _create_user_with_messenger(session, external_id=1)
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    link = f"tg://proxy?server=x&port=1&secret=ee{user.uuid.hex}abc"
    result, authorized = await authorize_by_link(
        user_repo, messenger_repo,
        Messenger.TELEGRAM, external_id=42, text=link,
    )

    assert result == AuthResult.OK
    assert authorized is not None
    assert authorized.id == user.id


async def test_authorize_by_link_sub_url(session):
    user = await _create_user_with_messenger(session, external_id=1)
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    link = f"https://example.com/sub/{user.uuid.hex}"
    result, authorized = await authorize_by_link(
        user_repo, messenger_repo,
        Messenger.TELEGRAM, external_id=43, text=link,
    )

    assert result == AuthResult.OK
    assert authorized.id == user.id


async def test_authorize_by_link_garbage(session):
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    result, authorized = await authorize_by_link(
        user_repo, messenger_repo,
        Messenger.TELEGRAM, external_id=1, text="hello world",
    )
    assert result == AuthResult.USER_NOT_FOUND
    assert authorized is None


async def test_authorize_by_link_none_uuid(session):
    """`str(None)` = 'None' — парсер вернёт None, потом UUID('None') упадёт."""
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    result, authorized = await authorize_by_link(
        user_repo, messenger_repo,
        Messenger.TELEGRAM, external_id=1, text="",
    )
    assert result == AuthResult.USER_NOT_FOUND
    assert authorized is None
