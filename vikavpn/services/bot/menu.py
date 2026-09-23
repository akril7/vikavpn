from enum import StrEnum


class BotMenu(StrEnum):
    AUTH = "auth"
    AUTH_WAIT_LINK = "auth_wait_link"
    REGISTER_PLATFORM = "register_platform"
    MAIN = "main"
    PROFILE = "profile"
    RENEW = "renew"
    RENEW_TARIFF = "renew_tariff"
    RENEW_DAYS = "renew_days"
    RENEW_TARGET = "renew_target"
    PAYMENT = "payment"
    HELP = "help"


class RenewMode(StrEnum):
    SELF = "self"
    SELF_AND_MANAGED = "self_and_managed"
    OTHER = "other"
