from datetime import timedelta
from decimal import Decimal

from src.core.payment.lifecycle import confirm_payment, create_payment, get_paid_payment
from src.core.users.flow.profile import build_profile
from src.core.users.flow.registration import register_user
from src.db.enums import Messenger, PaymentStatus, Tariff
from src.db.repo import (
    PaymentRepository,
    PaymentUserRepository,
    UserMessengerRepository,
    UserRepository, options,
)


async def test_full_registration_payment_flow(session, settings):
    """Полный сценарий: регистрация → продление через оплату → профиль."""
    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)
    payment_repo = PaymentRepository(session)
    link_repo = PaymentUserRepository(session)

    # 1. Регистрация
    user = await register_user(
        user_repo, messenger_repo,
        Messenger.TELEGRAM, external_id=111, ios_user=False,
    )
    await session.flush()

    assert user.is_active is True
    assert user.vpn_user is True
    assert user.proxy_user is True

    trial_expires = user.sub_expires_at

    # 2. Создание платежа на продление
    payment, url = await create_payment(
        payment_repo=payment_repo,
        link_repo=link_repo,
        payer=user,
        targets=[user],
        tariff=Tariff.PROXY,
        days=31,
        receiver=settings.yoomoney.receiver,
        fee_percent=settings.yoomoney.fee_percent,
    )

    assert payment.status == PaymentStatus.PENDING
    assert payment.amount == Decimal("72.10")
    assert "yoomoney.ru" in url

    # 3. Имитация вебхука — оплата подтверждена
    paid = await confirm_payment(
        user_repo, payment_repo, link_repo,
        label=payment.label, amount=payment.amount,
    )
    await session.flush()

    assert paid is not None
    assert paid.status == PaymentStatus.PAID

    # 4. Подписка продлена на 31 день
    refreshed = await user_repo.get_with(
        user.id,
        options=options.managed_options() + options.messenger_options(),
    )
    assert refreshed.sub_expires_at == trial_expires + timedelta(days=31)
    assert refreshed.vpn_user is False  # PROXY тариф
    assert refreshed.proxy_user is True

    # 5. get_paid_payment возвращает платёж
    assert await get_paid_payment(payment_repo, payment.label) is not None

    # 6. Профиль строится корректно
    # подгружаем связи, чтобы не ловить lazy="raise"
    refreshed = await user_repo.get_with(user.id, options=())
    refreshed.managed_links = []
    refreshed.messenger_links = await messenger_repo.list_by_user(user.id)

    profile = build_profile(refreshed, settings)
    assert profile.is_active is True
    assert profile.tariff_label == "TG Proxy"
    assert profile.tg_proxy_url is not None
    assert profile.clash_url is None


async def test_full_flow_with_managed_renewal(session, settings):
    """Проверяем SELF_AND_MANAGED через полный цикл."""
    from src.core.users.flow.renew import RenewMode, create_payment_for_renew
    from src.db.repo import UserManagementRepository

    user_repo = UserRepository(session)
    messenger_repo = UserMessengerRepository(session)

    # Регистрируем двух users, привязываем одного как managed к другому
    payer = await register_user(user_repo, messenger_repo, Messenger.TELEGRAM, 1, False)
    managed = await register_user(user_repo, messenger_repo, Messenger.TELEGRAM, 2, False)

    manage_repo = UserManagementRepository(session)
    await manage_repo.create(manager_id=payer.id, managed_id=managed.id)

    # Продление SELF_AND_MANAGED
    payment, _ = await create_payment_for_renew(
        user_repo,
        PaymentRepository(session),
        PaymentUserRepository(session),
        telegram_id=1,
        mode=RenewMode.SELF_AND_MANAGED,
        tariff=Tariff.FULL,
        days=31,
        receiver="recv",
        fee_percent=0,
    )
    assert payment.amount == 120 * 2

    # Платим
    await confirm_payment(
        user_repo,
        PaymentRepository(session),
        PaymentUserRepository(session),
        payment.label, payment.amount,
    )

    # Оба продлены на 31 день, оба с FULL
    for uid in (payer.id, managed.id):
        u = await user_repo.get(uid)
        assert u.vpn_user is True
        assert u.proxy_user is True
