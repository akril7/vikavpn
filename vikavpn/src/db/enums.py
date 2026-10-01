from enum import StrEnum


class Tariff(StrEnum):
    PROXY = "proxy"
    FULL = "full"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"


class Messenger(StrEnum):
    TELEGRAM = "telegram"
    VK = "vk"


def enum_values(enum_cls):
    return [member.value for member in enum_cls]
