# Архитектура проекта

Проект разбит на 7 модулей. Правило зависимостей — строго однонаправленное:

    cli ──► bootstrap ──► infrastructure ──► application ──► domain
     │           │                                │
     │           └──► configuration ◄─────────────┘
     └──► apps ──► bootstrap ──► infrastructure ──► application ──► domain


## Модули

| Модуль            | Назначение                                              |
|-------------------|---------------------------------------------------------|
| `configuration`   | Настройки из `.env`, `Settings`-агрегатор               |
| `domain`          | Чистое ядро: модели, enum'ы, правила, URL-билдеры       |
| `application`     | Use cases + порты (интерфейсы) к внешнему миру          |
| `infrastructure`  | Адаптеры: БД, systemd, docker, nginx, шаблоны, services |
| `bootstrap`       | Composition root: единственное место сборки адаптеров   |
| `apps`            | Запускаемые сервисы (aiohttp/aiogram)                   |
| `cli`             | Интерактивный CLI (questionary/rich)                    |


## Сводная таблица импортов
| Из \ В         | configuration | domain | application | infrastructure  | bootstrap | apps | cli |
|----------------|:-------------:|:------:|:-----------:|:---------------:|:---------:|:----:|:---:|
| configuration  |       ✅       |   ❌    |      ❌      |        ❌        |     ❌     |  ❌   |  ❌  |
| domain         |       ❌       |   ✅    |      ❌      |        ❌        |     ❌     |  ❌   |  ❌  |
| application    |   ✅ (типы)    |   ✅    |      ✅      |        ❌        |     ❌     |  ❌   |  ❌  |
| infrastructure |       ✅       |   ✅    |  ✅ (ports)  |        ✅        |     ❌     |  ❌   |  ❌  |
| bootstrap      |       ✅       |   ✅    |      ✅      |        ✅        |     ✅     |  ❌   |  ❌  |
| apps           |       ✅       |   ✅    |      ✅      | ✅ (persistence) |     ✅     |  ✅   |  ❌  |
| cli            |       ✅       |   ✅    |      ✅      | ✅ (persistence) |     ✅     |  ❌   |  ✅  |
