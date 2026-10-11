from datetime import timedelta

from src.core.users.flow.subscription import extend, set_expire
from src.core.utils.dt import utcnow
from src.db.enums import Tariff


def test_extend_active_subscription_adds_days_to_existing(make_user):
    user = make_user(days=10)
    old_expires = user.sub_expires_at

    extend(user, Tariff.PROXY, 31)

    assert user.sub_expires_at == old_expires + timedelta(days=31)


def test_extend_active_subscription_with_zero_days(make_user):
    user = make_user(days=10)
    old_expires = user.sub_expires_at

    extend(user, Tariff.PROXY, 0)

    assert user.sub_expires_at == old_expires


def test_extend_expired_subscription_starts_from_now(make_user):
    user = make_user(days=-5)
    before = utcnow()

    extend(user, Tariff.PROXY, 31)

    after = utcnow()
    expected_min = before + timedelta(days=31)
    expected_max = after + timedelta(days=31)
    assert expected_min <= user.sub_expires_at <= expected_max


def test_extend_expired_subscription_ignores_old_expiration(make_expired_user):
    user = make_expired_user(days=-100)
    old_expires = user.sub_expires_at

    extend(user, Tariff.PROXY, 30)

    # не должно быть old_expires + 30
    assert user.sub_expires_at > old_expires + timedelta(days=100)


def test_extend_with_full_sets_vpn_and_proxy(make_user):
    user = make_user(vpn_user=False, proxy_user=False)

    extend(user, Tariff.FULL, 30)

    assert user.vpn_user is True
    assert user.proxy_user is True


def test_extend_with_proxy_disables_vpn(make_user):
    user = make_user(vpn_user=True, proxy_user=False)

    extend(user, Tariff.PROXY, 30)

    assert user.vpn_user is False
    assert user.proxy_user is True


def test_extend_multiple_times_accumulates(make_user):
    user = make_user(days=1)  # точно в будущем
    start = user.sub_expires_at

    extend(user, Tariff.PROXY, 10)
    extend(user, Tariff.PROXY, 20)

    assert user.sub_expires_at == start + timedelta(days=30)


def test_set_expire_parses_datetime(make_user):
    user = make_user()

    set_expire(user, "01.01.2030 12:30")

    assert user.sub_expires_at.year == 2030
    assert user.sub_expires_at.month == 1
    assert user.sub_expires_at.day == 1
    assert user.sub_expires_at.hour == 12
    assert user.sub_expires_at.minute == 30
    assert user.sub_expires_at.tzinfo is not None


def test_set_expire_overrides_previous(make_user):
    user = make_user(days=1000)
    set_expire(user, "01.01.2025 00:00")
    assert user.sub_expires_at.year == 2025
