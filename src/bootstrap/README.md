# bootstrap

Composition root. Единственное место, где собираются конкретные адаптеры
из `configuration` и передаются в `application`/`cli`/`apps`.

## Назначение

- **`Registry`** — реализация `application.ports.registry.RegistryLike`.
  Знает про **все** конкретные адаптеры (`MitaInstaller`, `AppInstaller`,
  `SystemdUnitController`, …) и умеет их собирать из `Settings`.

## Пример

    from src.bootstrap.registry import Registry
    from src.configuration.aggregator import Settings

    settings = Settings()
    registry = Registry(settings)

    # registry можно передать в application.manager.* — они типизированы RegistryLike
    from src.application.manager import installation
    installation.install(registry, ["mita"])

## Правила

- `Registry` не содержит бизнес-логики — только геттеры.