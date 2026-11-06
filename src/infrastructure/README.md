# infrastructure

Адаптеры к внешнему миру: БД-сессии, репозитории, systemd, docker, subprocess,
nginx, шаблоны и конкретные сервисы (endpoint'ы, site, trustclient).

## Состав

    infrastructure/
      persistence/
        connection.py           # engine, Session, create_tables
        repo/
          base.py               # BaseRepository
          user.py               # UserRepository
          management.py         # UserManagementRepository
          messager.py           # UserMessengerRepository
          payment.py            # PaymentRepository
          payment_user.py       # PaymentUserRepository
          options.py            # selectinload-опции
      system/
        subprocess.py           # run_*, check_root, install_deb, ...
        systemctl.py            # SystemdUnit, daemon_reload
        docker.py               # docker-команды
      systemd.py                # SystemdUnitInstaller/Configurator/Controller
      app.py                    # AppInstaller/AppController (systemd-unit для apps)
      templating.py             # get_env (Jinja2)
      services/
        clash/                  # ClashConfigurator + render
        endpoints/              # Installer/Configurator/Controller + render
          mita/                 #
          hysteria/             # + auth/ + endpoint/
          trusttunnel/          # 
          mtproxyl/             # 
        site/                   # SiteInstaller + render
        trustclient/            # TrustClientInstaller + render

## Назначение

- **Реализации портов** из `application.ports.*`:
  `Installer`, `Controller`, `Configurator` — здесь.
- **Репозитории** — конкретные SQLAlchemy-запросы. Возвращают доменные модели.
- **Шаблоны** — Jinja2-рендер конфигов. Шаблоны лежат рядом с `render.py`.

## Пример

    from src.infrastructure.persistence.connection import Session
    from src.infrastructure.persistence.repo import UserRepository

    async with Session() as session:
        repo = UserRepository(session)
        user = await repo.get_by_uuid(uuid)

## Правила

- `infrastructure` **не импортирует** `application.manager`/`users`/`payment`.
  Знает только `application.ports`.
- Никакой бизнес-логики: «что делать с пользователями» — в `application`,
  «как записать файл/systemd-unit» — здесь.
