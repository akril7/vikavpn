from datetime import timedelta

import pytest

from src.core.users.flow.registration import (
    PASSWORD_ALPHABET,
    PASSWORD_LENGTH,
    TRIAL_DAYS,
    generate_password,
    register_user,
)
from src.core.utils.dt import utcnow
from src.db.enums import Messenger
from src.db.repo import UserMessengerRepository, UserRepository
from src.db.repo.messager import MessengerAlreadyBoundError


# ----- generate_password -----

def test_generate_password_length():
    assert len(generate_password()) == PASSWORD_LENGTH


def test_generate_password_charset():
    pwd = generate_password()
    assert all(c in PASSWORD_ALPHABET for c in pwd)


def test_generate_password_random():
    passwords = {generate_password() for _ in range(50)}
    assert len(passwords) == 50


# ----- register_user -----

async def test_register_user_creates_user_and_binds(session):
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    user = await register_user(
        user_repo, messenger_repo,
        Messenger.TELEGRAM, external_id=123456, ios_user=False,
    )

    assert user.id is not None
    assert user.vpn_user is True
    assert user.proxy_user is True
    assert user.ios_user is False

    link = await messenger_repo.get_by_external(Messenger.TELEGRAM, 123456)
    assert link is not None
    assert link.user_id == user.id


async def test_register_user_sets_trial_expiration(session):
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    before = utcnow()
    user = await register_user(
        user_repo, messenger_repo,
        Messenger.TELEGRAM, external_id=1, ios_user=False,
    )
    after = utcnow()

    expected_min = before + timedelta(days=TRIAL_DAYS)
    expected_max = after + timedelta(days=TRIAL_DAYS)
    assert expected_min <= user.sub_expires_at <= expected_max


async def test_register_user_generates_unique_name_and_uuid(session):
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    u1 = await register_user(user_repo, messenger_repo, Messenger.TELEGRAM, 1, False)
    u2 = await register_user(user_repo, messenger_repo, Messenger.TELEGRAM, 2, False)

    assert u1.name != u2.name
    assert u1.uuid != u2.uuid


async def test_register_user_with_ios_flag(session):
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    user = await register_user(
        user_repo, messenger_repo,
        Messenger.TELEGRAM, external_id=999, ios_user=True,
    )
    assert user.ios_user is True


async def test_register_user_twice_same_external_raises(session):
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    await register_user(user_repo, messenger_repo, Messenger.TELEGRAM, 555, False)
    with pytest.raises(MessengerAlreadyBoundError):
        await register_user(user_repo, messenger_repo, Messenger.TELEGRAM, 555, False)


async def test_register_user_password_is_generated(session):
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    user = await register_user(user_repo, messenger_repo, Messenger.TELEGRAM, 42, False)
    assert len(user.password) == PASSWORD_LENGTH
    assert all(c in PASSWORD_ALPHABET for c in user.password)
