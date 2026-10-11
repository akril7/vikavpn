from src.core.payment.plans import PLANS, get_plan, get_plans
from src.db.enums import Tariff


def test_get_plan_returns_expected_for_proxy_31():
    plan = get_plan(Tariff.PROXY, 31)
    assert plan is not None
    assert plan.price == 70
    assert plan.tariff == Tariff.PROXY
    assert plan.days == 31


def test_get_plan_returns_expected_for_full_31():
    plan = get_plan(Tariff.FULL, 31)
    assert plan is not None
    assert plan.price == 120


def test_get_plan_returns_none_for_unknown_days():
    assert get_plan(Tariff.PROXY, 999) is None


def test_get_plan_returns_none_for_unknown_tariff_days_combo():
    # days=186 есть для обоих тарифов, days=100 нет нигде
    assert get_plan(Tariff.FULL, 100) is None


def test_get_plans_returns_only_requested_tariff():
    proxy_plans = get_plans(Tariff.PROXY)
    assert all(p.tariff == Tariff.PROXY for p in proxy_plans)
    assert len(proxy_plans) == 4

    full_plans = get_plans(Tariff.FULL)
    assert all(p.tariff == Tariff.FULL for p in full_plans)
    assert len(full_plans) == 4


def test_plans_are_unique_by_tariff_and_days():
    keys = [(p.tariff, p.days) for p in PLANS]
    assert len(keys) == len(set(keys))


def test_full_tariff_more_expensive_than_proxy_for_same_days():
    for days in (31, 62, 93, 186):
        proxy = get_plan(Tariff.PROXY, days)
        full = get_plan(Tariff.FULL, days)
        assert full.price > proxy.price, f"days={days}"


def test_plans_prices_scale_linearly_with_days():
    # 2 месяца = 2 * 1 месяц, 3 месяца = 3 * 1 месяц, 6 = 6 * 1
    for tariff in (Tariff.PROXY, Tariff.FULL):
        p1 = get_plan(tariff, 31)
        p2 = get_plan(tariff, 62)
        p3 = get_plan(tariff, 93)
        p6 = get_plan(tariff, 186)
        assert p2.price == p1.price * 2
        assert p3.price == p1.price * 3
        assert p6.price == p1.price * 6


def test_plans_have_labels():
    for plan in PLANS:
        assert plan.label
        assert isinstance(plan.label, str)
