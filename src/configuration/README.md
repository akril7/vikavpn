# configuration

Настройки приложения из `.env`. Единственный модуль, который читает переменные окружения.

## Состав

    configuration/
      app.py            # BASE_DIR, FILES_DIR, DB_URL, DEBUG, TZ, ENV_PATH, LINK_DOMAIN
      base.py           # make_config(env_prefix) -> SettingsConfigDict
      aggregator.py     # Settings — ленивый агрегатор всех настроек
      other/
        clash.py        # ClashSettings
        mihomo.py       # MihomoSettings
        tls.py          # TLSSettings
        site/
          site.py       # SiteSettings
          nginx.py      # NginxSettings
      endpoints/
        mita.py         # MitaSettings, MitaProtocol
        hysteria.py     # HysteriaSettings
        trusttunnel.py  # TrustTunnelSettings
        mtproxyl.py     # MTProxyLSettings
      services/
        telegram.py     # TelegramBotSettings
        reloader.py     # ReloaderSettings
        payments.py     # PaymentsSettings
        yoomoney.py     # YoomoneySettings

## Назначение

- `Settings` — ленивый агрегатор: каждый подмодуль создаётся при первом обращении
  и кэшируется. Можно передать готовые экземпляры в конструктор (для тестов).
- Все остальные классы — `pydantic_settings.BaseSettings` с префиксом из `.env`.
- `make_config` — единая точка настройки `model_config` (env_file, frozen, extra="ignore").

## Пример

    from src.configuration.aggregator import Settings

    settings = Settings()
    print(settings.tls.domain)
    print(settings.reloader.url)   # лениво создаст ReloaderSettings

## Правила

- Один класс настроек — один домен ответственности.
- Все поля — с дефолтами или обязательные; валидация — через `pydantic`.
- Не импортировать сюда модели/репозитории — только примитивы и `Path`.
- `Settings` не должна тянуть `infrastructure`: если появится желание —
  значит, настройка относится к инфраструктуре и должна быть вынесена в адаптер.
