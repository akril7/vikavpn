# domain

Чистое ядро. Не знает ни про `.env`, ни про БД-сессии, ни про HTTP, ни про systemd.

## Состав

    domain/
      enums.py                  # Tariff, PaymentStatus, Messenger
      models/                   # SQLAlchemy-модели (доменные сущности)
        base.py                 # Base, IdMixin, CreateAtMixin
        user.py                 # User
        messenger.py            # UserMessenger
        payment.py              # Payment
        payment_user.py         # PaymentUser
      users/
        filters.py              # filter_vpn_users, filter_proxy_users
        subscription.py         # extend, set_expire
      payment/
        plans.py                # Plan, PLANS, get_plan(s)
      urls/
        file.py                 # build_origin, build_clash_config_url, ...
        link.py                 # build_telegram_proxy_url, parse_uuid_from_link, ...
      utils/
        dt.py                   # utcnow

## Правила

- Никаких `async`, никаких сетевых вызовов, никакого чтения файлов.
- Модели могут иметь `@property`, но не ходить в другие таблицы внутри них.
- Если нужен внешний ресурс (БД, HTTP, время из системы) — это `application`/`infrastructure`.
 