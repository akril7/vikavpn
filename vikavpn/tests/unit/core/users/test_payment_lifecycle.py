import uuid
from datetime import timedelta
from decimal import Decimal

import pytest

from src.core.payment.lifecycle import (
    confirm_payment,
    create_payment,
    get_paid_payment,
)
from src.core.utils.dt import utcnow
from src.db.enums import Messenger, PaymentStatus, Tariff
from src.db.repo import (
    PaymentRepository,
    PaymentUserRepository,
    UserMessengerRepository,
    UserRepository,
)


async def _create_user(session, *, telegram_id=None, days=5):
    user_repo = UserRepository(session)
    user = await user_repo.create(
        name=f"u_{uuid.uuid4().hex[:8]}",
        password="pwd",
        uuid=uuid.uuid4(),
        sub_expires_at=utcnow() + timedelta(days=days),
    )
    if telegram_id is not None:
        messenger_repo = UserMessengerRepository(session)
        await messenger_repo.bind(
            user_id=user.id,
            messenger=Messenger.TELEGRAM,
            external_id=telegram_id,
        )
    return user


# ----- create_payment -----

async def test_create_payment_calculates_amount_without_fee(session):
    payer = await _create_user(session, telegram_id=1)
    payment, url = await create_payment(
        payment_repo=PaymentRepository(session),
        link_repo=PaymentUserRepository(session),
        payer=payer,
        targets=[payer],
        tariff=Tariff.PROXY,
        days=31,
        receiver="recv",
        fee_percent=0,
    )

    assert payment.amount == Decimal("70.00")
    assert payment.status == PaymentStatus.PENDING
    assert payment.label == f"{payer.uuid.hex}_{Tariff.PROXY.value}_{payment.id}"
    assert "yoomoney.ru" in url


async def test_create_payment_calculates_amount_with_fee(session):
    payer = await _create_user(session, telegram_id=1)

    payment, _ = await create_payment(
        payment_repo=PaymentRepository(session),
        link_repo=PaymentUserRepository(session),
        payer=payer,
        targets=[payer],
        tariff=Tariff.PROXY,
        days=31,
        receiver="recv",
        fee_percent=3.0,
    )

    # 70 + 3% = 72.10
    assert payment.amount == Decimal("72.10")


async def test_create_payment_multiplies_by_targets(session):
    payer = await _create_user(session, telegram_id=1)
    t1 = await _create_user(session)
    t2 = await _create_user(session)

    payment, _ = await create_payment(
        payment_repo=PaymentRepository(session),
        link_repo=PaymentUserRepository(session),
        payer=payer,
        targets=[payer, t1, t2],
        tariff=Tariff.FULL,
        days=31,
        receiver="recv",
        fee_percent=0,
    )

    assert payment.amount == 120 * 3


async def test_create_payment_links_all_targets(session):
    payer = await _create_user(session, telegram_id=1)
    t1 = await _create_user(session)
    t2 = await _create_user(session)

    link_repo = PaymentUserRepository(session)
    payment, _ = await create_payment(
        payment_repo=PaymentRepository(session),
        link_repo=link_repo,
        payer=payer,
        targets=[payer, t1, t2],
        tariff=Tariff.PROXY,
        days=31,
        receiver="recv",
    )

    ids = set(await link_repo.get_user_ids(payment.id))
    assert ids == {payer.id, t1.id, t2.id}


async def test_create_payment_rejects_empty_targets(session):
    payer = await _create_user(session, telegram_id=1)

    with pytest.raises(ValueError):
        await create_payment(
            payment_repo=PaymentRepository(session),
            link_repo=PaymentUserRepository(session),
            payer=payer,
            targets=[],
            tariff=Tariff.PROXY,
            days=31,
            receiver="recv",
        )


async def test_create_payment_rejects_unknown_plan(session):
    payer = await _create_user(session, telegram_id=1)

    with pytest.raises(ValueError):
        await create_payment(
            payment_repo=PaymentRepository(session),
            link_repo=PaymentUserRepository(session),
            payer=payer,
            targets=[payer],
            tariff=Tariff.PROXY,
            days=999,
            receiver="recv",
        )


# ----- confirm_payment -----

async def test_confirm_payment_unknown_label(session):
    result = await confirm_payment(
        UserRepository(session),
        PaymentRepository(session),
        PaymentUserRepository(session),
        label="nonexistent",
        amount=Decimal("1.00"),
    )
    assert result is None


async def test_confirm_payment_wrong_amount_returns_none(session):
    payer = await _create_user(session, telegram_id=1)
    payment_repo = PaymentRepository(session)
    link_repo = PaymentUserRepository(session)

    payment, _ = await create_payment(
        payment_repo=payment_repo,
        link_repo=link_repo,
        payer=payer,
        targets=[payer],
        tariff=Tariff.PROXY,
        days=31,
        receiver="recv",
    )

    result = await confirm_payment(
        UserRepository(session), payment_repo, link_repo,
        label=payment.label, amount=Decimal("1.00"),
    )
    assert result is None

    # статус не изменился
    refreshed = await payment_repo.get_by_label(payment.label)
    assert refreshed.status == PaymentStatus.PENDING


async def test_confirm_payment_marks_paid_and_extends_targets(session):
    payer = await _create_user(session, telegram_id=1, days=5)
    target = await _create_user(session, days=5)
    expires_before_payer = payer.sub_expires_at
    expires_before_target = target.sub_expires_at

    payment_repo = PaymentRepository(session)
    link_repo = PaymentUserRepository(session)

    payment, _ = await create_payment(
        payment_repo=payment_repo,
        link_repo=link_repo,
        payer=payer,
        targets=[payer, target],
        tariff=Tariff.PROXY,
        days=31,
        receiver="recv",
        fee_percent=0,
    )

    paid = await confirm_payment(
        UserRepository(session), payment_repo, link_repo,
        label=payment.label, amount=payment.amount,
    )

    assert paid is not None
    assert paid.status == PaymentStatus.PAID
    assert paid.paid_at is not None

    refreshed_payer = await UserRepository(session).get(payer.id)
    refreshed_target = await UserRepository(session).get(target.id)

    assert refreshed_payer.sub_expires_at == expires_before_payer + timedelta(days=31)
    assert refreshed_target.sub_expires_at == expires_before_target + timedelta(days=31)


async def test_confirm_payment_full_tariff_sets_vpn(session):
    payer = await _create_user(session, telegram_id=1, days=5)
    payer.vpn_user = False
    payer.proxy_user = False
    await session.flush()

    payment_repo = PaymentRepository(session)
    link_repo = PaymentUserRepository(session)

    payment, _ = await create_payment(
        payment_repo=payment_repo,
        link_repo=link_repo,
        payer=payer,
        targets=[payer],
        tariff=Tariff.FULL,
        days=31,
        receiver="recv",
    )

    await confirm_payment(
        UserRepository(session), payment_repo, link_repo,
        label=payment.label, amount=payment.amount,
    )

    refreshed = await UserRepository(session).get(payer.id)
    assert refreshed.vpn_user is True
    assert refreshed.proxy_user is True


async def test_confirm_payment_is_idempotent(session):
    """Второй вызов с тем же label не должен продлить дважды."""
    payer = await _create_user(session, telegram_id=1, days=5)
    payment_repo = PaymentRepository(session)
    link_repo = PaymentUserRepository(session)

    payment, _ = await create_payment(
        payment_repo=payment_repo,
        link_repo=link_repo,
        payer=payer,
        targets=[payer],
        tariff=Tariff.PROXY,
        days=31,
        receiver="recv",
    )

    p1 = await confirm_payment(
        UserRepository(session), payment_repo, link_repo,
        payment.label, payment.amount,
    )
    expires_after_first = (await UserRepository(session).get(payer.id)).sub_expires_at

    p2 = await confirm_payment(
        UserRepository(session), payment_repo, link_repo,
        payment.label, payment.amount,
    )
    expires_after_second = (await UserRepository(session).get(payer.id)).sub_expires_at

    assert p1.id == p2.id
    assert expires_after_first == expires_after_second


async def test_confirm_payment_already_paid_returns_payment(session):
    payer = await _create_user(session, telegram_id=1, days=5)
    payment_repo = PaymentRepository(session)
    link_repo = PaymentUserRepository(session)

    payment, _ = await create_payment(
        payment_repo=payment_repo,
        link_repo=link_repo,
        payer=payer,
        targets=[payer],
        tariff=Tariff.PROXY,
        days=31,
        receiver="recv",
    )

    first = await confirm_payment(
        UserRepository(session), payment_repo, link_repo,
        payment.label, payment.amount,
    )
    second = await confirm_payment(
        UserRepository(session), payment_repo, link_repo,
        payment.label, payment.amount,
    )
    assert second is not None
    assert second.id == first.id
    assert second.status == PaymentStatus.PAID


# ----- get_paid_payment -----

async def test_get_paid_payment_returns_none_for_pending(session):
    payer = await _create_user(session, telegram_id=1)
    payment_repo = PaymentRepository(session)

    payment, _ = await create_payment(
        payment_repo=payment_repo,
        link_repo=PaymentUserRepository(session),
        payer=payer,
        targets=[payer],
        tariff=Tariff.PROXY,
        days=31,
        receiver="recv",
    )

    assert await get_paid_payment(payment_repo, payment.label) is None


async def test_get_paid_payment_returns_paid(session):
    payer = await _create_user(session, telegram_id=1, days=5)
    payment_repo = PaymentRepository(session)
    link_repo = PaymentUserRepository(session)

    payment, _ = await create_payment(
        payment_repo=payment_repo,
        link_repo=link_repo,
        payer=payer,
        targets=[payer],
        tariff=Tariff.PROXY,
        days=31,
        receiver="recv",
    )

    await confirm_payment(
        UserRepository(session), payment_repo, link_repo,
        payment.label, payment.amount,
    )

    paid = await get_paid_payment(payment_repo, payment.label)
    assert paid is not None
    assert paid.status == PaymentStatus.PAID


async def test_get_paid_payment_unknown_label(session):
    assert await get_paid_payment(PaymentRepository(session), "unknown") is None
