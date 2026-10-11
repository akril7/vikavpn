import uuid

import pytest

from src.core.users.flow.renew import (
    PayerNotFoundError,
    RenewMode,
    TargetNotFoundError,
    create_payment_for_renew,
)
from src.db.enums import Messenger, Tariff
from src.db.repo import (
    PaymentRepository,
    PaymentUserRepository,
    UserManagementRepository,
    UserMessengerRepository,
    UserRepository,
)


async def _create_user(session, *, telegram_id: int | None = None):
    user_repo = UserRepository(session)
    user = await user_repo.create(
        name=f"u_{uuid.uuid4().hex[:8]}",
        password="pwd",
        uuid=uuid.uuid4(),
    )
    if telegram_id is not None:
        messenger_repo = UserMessengerRepository(session)
        await messenger_repo.bind(
            user_id=user.id,
            messenger=Messenger.TELEGRAM,
            external_id=telegram_id,
        )
    return user


async def _link(session, manager_id: int, managed_id: int):
    repo = UserManagementRepository(session)
    await repo.create(manager_id=manager_id, managed_id=managed_id)


# ----- SELF -----

async def test_renew_self_creates_payment_for_self(session):
    user = await _create_user(session, telegram_id=1)

    payment, url = await create_payment_for_renew(
        UserRepository(session),
        PaymentRepository(session),
        PaymentUserRepository(session),
        telegram_id=1,
        mode=RenewMode.SELF,
        tariff=Tariff.PROXY,
        days=31,
        receiver="recv",
        fee_percent=0,
    )

    assert payment.id is not None
    assert payment.amount == 70
    assert "yoomoney.ru" in url

    user_ids = await PaymentUserRepository(session).get_user_ids(payment.id)
    assert user_ids == [user.id]


# ----- SELF_AND_MANAGED -----

async def test_renew_self_and_managed_includes_all(session):
    payer = await _create_user(session, telegram_id=1)
    m1 = await _create_user(session)
    m2 = await _create_user(session)
    await _link(session, payer.id, m1.id)
    await _link(session, payer.id, m2.id)

    payment, _ = await create_payment_for_renew(
        UserRepository(session),
        PaymentRepository(session),
        PaymentUserRepository(session),
        telegram_id=1,
        mode=RenewMode.SELF_AND_MANAGED,
        tariff=Tariff.PROXY,
        days=31,
        receiver="recv",
        fee_percent=0,
    )

    ids = set(await PaymentUserRepository(session).get_user_ids(payment.id))
    assert ids == {payer.id, m1.id, m2.id}
    assert payment.amount == 70 * 3


async def test_renew_self_and_managed_without_managed(session):
    payer = await _create_user(session, telegram_id=1)

    payment, _ = await create_payment_for_renew(
        UserRepository(session),
        PaymentRepository(session),
        PaymentUserRepository(session),
        telegram_id=1,
        mode=RenewMode.SELF_AND_MANAGED,
        tariff=Tariff.PROXY,
        days=31,
        receiver="recv",
        fee_percent=0,
    )

    ids = await PaymentUserRepository(session).get_user_ids(payment.id)
    assert ids == [payer.id]


# ----- OTHER -----

async def test_renew_other_requires_target_id(session):
    await _create_user(session, telegram_id=1)

    with pytest.raises(TargetNotFoundError):
        await create_payment_for_renew(
            UserRepository(session),
            PaymentRepository(session),
            PaymentUserRepository(session),
            telegram_id=1,
            mode=RenewMode.OTHER,
            tariff=Tariff.PROXY,
            days=31,
            receiver="recv",
            target_id=None,
        )


async def test_renew_other_with_unknown_target(session):
    await _create_user(session, telegram_id=1)

    with pytest.raises(TargetNotFoundError):
        await create_payment_for_renew(
            UserRepository(session),
            PaymentRepository(session),
            PaymentUserRepository(session),
            telegram_id=1,
            mode=RenewMode.OTHER,
            tariff=Tariff.PROXY,
            days=31,
            receiver="recv",
            target_id=999999,
        )


async def test_renew_other_picks_managed(session):
    payer = await _create_user(session, telegram_id=1)
    managed = await _create_user(session)
    await _link(session, payer.id, managed.id)

    payment, _ = await create_payment_for_renew(
        UserRepository(session),
        PaymentRepository(session),
        PaymentUserRepository(session),
        telegram_id=1,
        mode=RenewMode.OTHER,
        tariff=Tariff.FULL,
        days=31,
        receiver="recv",
        target_id=managed.id,
    )

    ids = await PaymentUserRepository(session).get_user_ids(payment.id)
    assert ids == [managed.id]
    assert payment.amount == 120


async def test_renew_other_cannot_pick_unrelated_user(session):
    payer = await _create_user(session, telegram_id=1)
    stranger = await _create_user(session)

    with pytest.raises(TargetNotFoundError):
        await create_payment_for_renew(
            UserRepository(session),
            PaymentRepository(session),
            PaymentUserRepository(session),
            telegram_id=1,
            mode=RenewMode.OTHER,
            tariff=Tariff.PROXY,
            days=31,
            receiver="recv",
            target_id=stranger.id,
        )


# ----- errors -----

async def test_renew_payer_not_found(session):
    with pytest.raises(PayerNotFoundError):
        await create_payment_for_renew(
            UserRepository(session),
            PaymentRepository(session),
            PaymentUserRepository(session),
            telegram_id=999,
            mode=RenewMode.SELF,
            tariff=Tariff.PROXY,
            days=31,
            receiver="recv",
        )


# ----- fee -----

async def test_renew_fee_percent_applied(session):
    await _create_user(session, telegram_id=1)

    payment, _ = await create_payment_for_renew(
        UserRepository(session),
        PaymentRepository(session),
        PaymentUserRepository(session),
        telegram_id=1,
        mode=RenewMode.SELF,
        tariff=Tariff.PROXY,
        days=31,
        receiver="recv",
        fee_percent=10.0,
    )

    assert payment.amount == 77  # 70 + 10%


async def test_renew_fee_percent_zero(session):
    await _create_user(session, telegram_id=1)

    payment, _ = await create_payment_for_renew(
        UserRepository(session),
        PaymentRepository(session),
        PaymentUserRepository(session),
        telegram_id=1,
        mode=RenewMode.SELF,
        tariff=Tariff.PROXY,
        days=31,
        receiver="recv",
        fee_percent=0,
    )

    assert payment.amount == 70
