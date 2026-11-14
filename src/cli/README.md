# cli

Интерактивный CLI на `questionary` + `rich`. Точка входа — `manage.py`.

## Состав

    cli/
      __main__.py           # main() — обёртка над run(), ловит KeyboardInterrupt
      app.py                # run() — цикл главного меню + _dispatch
      state.py              # CliContext (settings + registry, reload())
      console.py            # ok/warn/err/info/muted, print_header, clear
      async_runtime.py      # AsyncRuntime: event loop в отдельном потоке
      actions/              # use cases CLI (тонкие обёртки)
        users/              # crud-like
          create.py
          delete.py
          get.py
          messenger.py
          mutations.py
          utils.py
        components.py       # install/uninstall/setup/installed_status
        configure.py        # apply/restart_all/trigger_reload/open_env_and_maybe_restart
        services.py         # status/start/stop/restart/reload
      menu/                 # экраны меню
        main.py,
        components.py
        configure.py
        services.py
        users.py
        user_edit.py
      widgets/              # переиспользуемые виджеты
        prompts.py          # select/checkbox/confirm/text/password/pause
        tables.py           # users_table/services_table/installed_table/kv_table
        logs.py             # live-tail journalctl
      utils/
        editor.py           # edit_env (открыть .env в $EDITOR)
        systemd.py          # list_units (список сервисов для логов)

## Назначение

- **`actions/*`** — тонкие обёртки: вызвать `application.manager.*` или
  `application.users.*`, обернуть в `console.status`, вернуть bool.
- **`menu/*`** — экраны: рисуют таблицы/списки, зовут `prompts.*`,
  диспатчат в `actions.*`.
- **`widgets/*`** — переиспользуемые элементы (prompt-ы, таблицы, live-логи).
- **`CliContext`** — держит `Settings` и `Registry`, умеет `reload()`
  (пересоздать оба после редактирования `.env`).

## Правила

- `actions/*` не содержит бизнес-логики — только вызов use case + вывод.
- `menu/*` не лезет в БД напрямую — только через `actions.*`.
- `widgets/*` не знает про `Settings`/`Registry` — принимает примитивы.
- `cli` может импортировать `infrastructure.persistence.connection.Session` —
  это composition root уровня запроса. Но `infrastructure.services.*` — только
  через `bootstrap`.
