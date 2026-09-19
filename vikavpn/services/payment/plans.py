from dataclasses import dataclass

from database.models import Tariff


@dataclass(frozen=True)
class Plan:
    tariff: Tariff
    days: int
    price: int
    label: str


PLANS: list[Plan] = [
    Plan(Tariff.PROXY, 30, 70, "1 месяц"),
    Plan(Tariff.PROXY, 60, 140, "2 месяца"),
    Plan(Tariff.PROXY, 90, 210, "3 месяца"),
    Plan(Tariff.PROXY, 180, 420, "6 месяцев"),
    Plan(Tariff.FULL, 30, 120, "1 месяц"),
    Plan(Tariff.FULL, 60, 240, "2 месяца"),
    Plan(Tariff.FULL, 90, 360, "3 месяца"),
    Plan(Tariff.FULL, 180, 720, "6 месяцев"),
]


def get_plans(tariff: Tariff) -> list[Plan]:
    return [plan for plan in PLANS if plan.tariff == tariff]


def get_plan(tariff: Tariff, days: int) -> Plan | None:
    for plan in PLANS:
        if plan.tariff == tariff and plan.days == days:
            return plan
    return None
