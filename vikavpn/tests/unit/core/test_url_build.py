import uuid
from decimal import Decimal

from src.core.url_build.link import (
    build_bot_auth_url,
    build_payment_url,
    build_telegram_proxy_url,
    parse_uuid_from_link,
)
from src.core.url_build.file import (
    build_clash_config_url,
    build_clash_video_guide_url,
    build_origin,
)


# ----- parse_uuid_from_link -----

def test_parse_uuid_from_tg_proxy_link():
    uid = uuid.uuid4()
    link = f"tg://proxy?server=example.com&port=443&secret=ee{uid.hex}snihex"
    assert parse_uuid_from_link(link) == uid


def test_parse_uuid_from_tg_proxy_link_uppercase():
    uid = uuid.uuid4()
    link = f"tg://proxy?server=x&port=1&secret=ee{uid.hex.upper()}"
    assert parse_uuid_from_link(link) == uid


def test_parse_uuid_from_sub_link():
    uid = uuid.uuid4()
    link = f"https://example.com/sub/{uid.hex}"
    assert parse_uuid_from_link(link) == uid


def test_parse_uuid_returns_none_on_garbage():
    assert parse_uuid_from_link("hello world") is None
    assert parse_uuid_from_link("") is None
    assert parse_uuid_from_link("tg://proxy?server=x") is None


def test_parse_uuid_returns_none_on_short_hex():
    assert parse_uuid_from_link("tg://proxy?secret=eeabc") is None


# ----- build_telegram_proxy_url -----

def test_build_telegram_proxy_url_format(make_user):
    user = make_user()
    url = build_telegram_proxy_url(
        user, sni="example.com", domain="test.local", port=443,
    )
    assert url.startswith("tg://proxy?")
    assert f"server=test.local" in url
    assert "port=443" in url
    assert f"secret=ee{user.uuid.hex}" in url
    # SNI закодирован в hex
    assert "example.com".encode().hex() in url


# ----- build_bot_auth_url -----

def test_build_bot_auth_url(make_user):
    user = make_user()
    url = build_bot_auth_url("my_bot", user)
    assert url == f"https://t.me/my_bot?start={user.uuid.hex}"


# ----- build_payment_url -----

def test_build_payment_url_contains_fields(make_payment):
    payment = make_payment(payer_id=1, amount=Decimal("123.45"), label="abc_1")
    url = build_payment_url(payment, receiver="my-receiver")
    assert "https://yoomoney.ru/quickpay/confirm.xml" in url
    assert "receiver=my-receiver" in url
    assert "sum=123.45" in url
    assert "label=abc_1" in url
    assert "quickpay-form=button" in url


# ----- file url_build -----

def test_build_origin_default_port():
    assert build_origin("example.com", 443) == "https://example.com"


def test_build_origin_custom_port():
    assert build_origin("example.com", 8443) == "https://example.com:8443"


def test_build_clash_config_url(make_user):
    user = make_user()
    url = build_clash_config_url(user, "https://example.com", "/sub/")
    assert url == f"https://example.com/sub/{user.uuid.hex}"


def test_build_clash_video_guide_url():
    url = build_clash_video_guide_url("https://example.com")
    assert url == "https://example.com/files/guides/clashmi.mp4"
