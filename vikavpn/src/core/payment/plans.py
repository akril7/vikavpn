from dataclasses import dataclass

from src.db.enums import Tariff


@dataclass(frozen=True)
class Plan:
    tariff: Tariff
    days: int
    price: int
    label: str


PLANS: list[Plan] = [
    Plan(Tariff.PROXY, 31, 70, "1 месяц"),
    Plan(Tariff.PROXY, 62, 140, "2 месяца"),
    Plan(Tariff.PROXY, 93, 210, "3 месяца"),
    Plan(Tariff.PROXY, 186, 420, "6 месяцев"),
    Plan(Tariff.FULL, 31, 120, "1 месяц"),
    Plan(Tariff.FULL, 62, 240, "2 месяца"),
    Plan(Tariff.FULL, 93, 360, "3 месяца"),
    Plan(Tariff.FULL, 186, 720, "6 месяцев"),
]


def get_plans(tariff: Tariff) -> list[Plan]:
    return [plan for plan in PLANS if plan.tariff == tariff]


def get_plan(tariff: Tariff, days: int) -> Plan | None:
    for plan in PLANS:
        if plan.tariff == tariff and plan.days == days:
            return plan
    return None
