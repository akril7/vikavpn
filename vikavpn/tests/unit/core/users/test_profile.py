import uuid
from datetime import timedelta

from src.core.users.flow.profile import build_profile, tariff_label
from src.core.utils.dt import utcnow
from src.db.models import User


def _user(*, vpn=True, proxy=True, days=10, name="test"):
    return User(
        name=name,
        uuid=uuid.uuid4(),
        password="p",
        sub_expires_at=utcnow() + timedelta(days=days),
        vpn_user=vpn,
        proxy_user=proxy,
    )


# ----- tariff_label -----

def test_tariff_label_both():
    assert tariff_label(_user(vpn=True, proxy=True)) == "VPN + TG Proxy"


def test_tariff_label_vpn_only():
    assert tariff_label(_user(vpn=True, proxy=False)) == "VPN"


def test_tariff_label_proxy_only():
    assert tariff_label(_user(vpn=False, proxy=True)) == "TG Proxy"


def test_tariff_label_none():
    assert tariff_label(_user(vpn=False, proxy=False)) == "—"


# ----- build_profile -----
# build_profile читает user.managed_links и user.messenger_links
# (lazy="raise"). Поэтому обходимся ручным заполнением.

def _prepare(user: User) -> User:
    """Эмулируем загруженные связи, чтобы не ловить lazy='raise'."""
    user.managed_links = []
    user.messenger_links = []
    return user


def test_build_profile_basic_fields(settings):
    user = _prepare(_user(vpn=True, proxy=True, days=10))

    profile = build_profile(user, settings)

    assert profile.name == user.name
    assert profile.password == user.password
    assert profile.is_active is True
    assert profile.days_left >= 9
    assert profile.tariff_label == "VPN + TG Proxy"


def test_build_profile_urls_both(settings):
    user = _prepare(_user(vpn=True, proxy=True))

    profile = build_profile(user, settings)

    assert profile.clash_url is not None
    assert profile.tg_proxy_url is not None
    assert profile.clash_url.endswith(user.uuid.hex)
    assert f"secret=ee{user.uuid.hex}" in profile.tg_proxy_url


def test_build_profile_only_vpn(settings):
    user = _prepare(_user(vpn=True, proxy=False))

    profile = build_profile(user, settings)

    assert profile.clash_url is not None
    assert profile.tg_proxy_url is None


def test_build_profile_only_proxy(settings):
    user = _prepare(_user(vpn=False, proxy=True))

    profile = build_profile(user, settings)

    assert profile.clash_url is None
    assert profile.tg_proxy_url is not None


def test_build_profile_no_urls(settings):
    user = _prepare(_user(vpn=False, proxy=False))

    profile = build_profile(user, settings)

    assert profile.clash_url is None
    assert profile.tg_proxy_url is None


def test_build_profile_days_left_zero_for_expired(settings):
    user = _prepare(_user(days=-3))

    profile = build_profile(user, settings)

    assert profile.days_left == 0
    assert profile.is_active is False


def test_build_profile_includes_managed_names(settings):
    user = _prepare(_user())
    managed = _user(name="managed_1")

    from src.db.models import UserManagement
    link = UserManagement(manager_id=1, managed_id=2)
    link.managed = managed
    user.managed_links = [link]

    profile = build_profile(user, settings)

    assert profile.managed_names == ["managed_1"]


def test_build_profile_telegram_id_none_without_links(settings):
    user = _prepare(_user())

    profile = build_profile(user, settings)

    assert profile.telegram_id is None
