# apps

Запускаемые сервисы.
Каждый подпакет — самостоятельная точка входа (`python -m src.apps.<name>`).

## Состав

    apps/
      hysteria_auth/        # POST /auth — проверка логин:пароль
      payments/             # POST /payments/yoomoney — webhook ЮMoney
      reloader/             # /reload, /flush + планировщик expiry
      telegram_bot/         # aiogram-бот (handlers, keyboards, states, tasks)

## Назначение

- **Тонкие точки входа**: собрать приложение, повесить роуты/хендлеры,
  запустить event loop.
- Могут импортировать `bootstrap` (сборка), `application` (use cases),
  `infrastructure.persistence` (сессии/репозитории)
- **Не содержат бизнес-логики**: логика — в `application`, адаптеры — в
  `infrastructure`

## Пример

    # apps/reloader/__main__.py
    from src.bootstrap.composition import build_reloader_subsystem
    from src.configuration.aggregator import Settings

    def main(settings: Settings) -> None:
        _, reloader, expiry = build_reloader_subsystem(settings)
        # ... web.run_app(...)
