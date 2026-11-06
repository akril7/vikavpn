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

## Правила

- `domain` не импортирует ничего из `src`, кроме `src.domain`.
- `application` импортирует только `domain`, `configuration`.
- `infrastructure` импортирует только `domain`, `configuration`. 
- `bootstrap` — единственный, кто импортирует `infrastructure`
- `apps` и `cli` — composition roots, им можно `bootstrap` + `application` + `infrastructure.persistence`.

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

## Проверка

1. infrastructure не тянет application.manager/users/payment \
`grep -rn "from src.application\.\(manager\|users\|payment\)" src/infrastructure/ && echo FAIL`

2. application не тянет infrastructure (кроме типа AsyncSession — это sqlalchemy) \
`grep -rn "from src.infrastructure" src/application/ && echo FAIL`

3. domain не тянет ничего из src, кроме src.domain \
`grep -rn "from src\." src/domain/ | grep -v "from src.domain" && echo FAIL `
