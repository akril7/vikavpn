# application

Прикладной слой: use cases и порты (интерфейсы) к внешнему миру.
Оркестрирует `domain`, но не знает, **кто именно** реализует порты.

## Состав

    application/
      ports/                    # интерфейсы (Protocol/ABC) к внешнему миру
        repo/                   # RepoLike классы
          user.py                 # for User
          messenger.py            # for UserMessenger
          payment.py              # for Payment
          payment_user.py         # for PaymentUser
        services/
          installer.py            # Installer (install/uninstall/is_installed)
          controller.py           # Controller (status/start/stop/restart/reload)
          configurator.py         # Configurator (apply(users))
          errors.py               # ServiceError и подклассы
      manager/                  # оркестрация через порты
        installation.py           # install/uninstall/get_installed(registry, names)
        configure.py              # apply/apply_active_users/build_reloader(registry, ...)
        control.py                # status/start/stop/restart/reload(registry, names)
      lifecycle/
        reloader.py               # Reloader (debounce + max_delay)
        scheduler.py              # ExpiryScheduler (читает UserRepository)
      users/
        registration.py           # register_user, generate_password
        auth.py                   # authorize_by_uuid, authorize_by_link
        profile.py                # build_profile, ProfileView
        renew.py                  # create_payment_for_renew, RenewMode
        importer.py               # import_users_from_file
      payment/
        lifecycle.py              # create_payment, confirm_payment, get_paid_payment
      urls/                     # сборка url-ов через Settings
        file.py                   # build_clash_config_url, build_clash_video_guide_url
        link.py                   # build_telegram_proxy_url, build_bot_auth_url, build_payment_url

## Назначение

- **Порты** — единственное, что видит `infrastructure`. Реализации живут там.
- **Use cases** — сценарии: «зарегистрировать пользователя», «подтвердить оплату»,
  «применить конфигурацию», «перезапустить сервис».
- **`manager/*`** — тонкая оркестрация: перебрать `registry.get_*_targets()`
  и вызвать методы портов. Не знает про systemd/docker/nginx.

## Пример

    from src.application.manager import installation
    from src.application.ports.registry import RegistryLike

    def setup(registry: RegistryLike) -> None:
        installation.uninstall(registry, None)
        installation.install(registry, None)

## Правила

- `application` **не импортирует** `infrastructure`. Если нужен адаптер —
  принимай его как аргумент типа из `ports/`.
