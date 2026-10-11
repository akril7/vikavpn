import uuid
from datetime import timedelta
from decimal import Decimal

import pytest

from src.core.utils.dt import utcnow
from src.db.enums import Messenger, PaymentStatus, Tariff
from src.db.models import Payment, User, UserManagement, UserMessenger


def _make_user(
    *,
    name: str | None = None,
    password: str = "secret123",
    days: int = 30,
    vpn_user: bool = True,
    proxy_user: bool = True,
    ios_user: bool = False,
) -> User:
    return User(
        name=name or f"user_{uuid.uuid4().hex[:8]}",
        uuid=uuid.uuid4(),
        password=password,
        sub_expires_at=utcnow() + timedelta(days=days),
        vpn_user=vpn_user,
        proxy_user=proxy_user,
        ios_user=ios_user,
    )


@pytest.fixture
def make_user():
    return _make_user


@pytest.fixture
def make_expired_user():
    def _factory(**kw):
        kw.setdefault("days", -1)
        return _make_user(**kw)
    return _factory


@pytest.fixture
def make_payment():
    def _factory(
        payer_id: int,
        *,
        amount: Decimal | str = Decimal("100.00"),
        days: int = 30,
        tariff: Tariff = Tariff.PROXY,
        label: str | None = None,
    ) -> Payment:
        return Payment(
            payer_id=payer_id,
            tariff=tariff,
            days=days,
            amount=Decimal(amount),
            label=label or f"{uuid.uuid4().hex}_label",
            status=PaymentStatus.PENDING,
        )
    return _factory


@pytest.fixture
def make_messenger():
    def _factory(
        user_id: int,
        *,
        messenger: Messenger = Messenger.TELEGRAM,
        external_id: int | None = None,
    ) -> UserMessenger:
        return UserMessenger(
            user_id=user_id,
            messenger=messenger,
            external_id=(
                external_id if external_id is not None
                else uuid.uuid4().int % 10**9
            ),
        )
    return _factory


@pytest.fixture
def make_management():
    def _factory(manager_id: int, managed_id: int) -> UserManagement:
        return UserManagement(manager_id=manager_id, managed_id=managed_id)
    return _factory
