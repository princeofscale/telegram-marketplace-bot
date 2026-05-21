# Telegram Marketplace Bot

![CodeRabbit Pull Request Reviews](https://img.shields.io/coderabbit/prs/github/princeofscale/telegram-marketplace-bot?utm_source=oss&utm_medium=github&utm_campaign=princeofscale%2Ftelegram-marketplace-bot&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews)
[![Linting](https://github.com/princeofscale/telegram-marketplace-bot/actions/workflows/linters.yml/badge.svg)](https://github.com/princeofscale/telegram-marketplace-bot/actions/workflows/linters.yml)
[![CodeQL](https://github.com/princeofscale/telegram-marketplace-bot/actions/workflows/codeql.yml/badge.svg)](https://github.com/princeofscale/telegram-marketplace-bot/actions/workflows/codeql.yml)
[![OpenSSF Scorecard](https://github.com/princeofscale/telegram-marketplace-bot/actions/workflows/scorecard.yml/badge.svg)](https://github.com/princeofscale/telegram-marketplace-bot/actions/workflows/scorecard.yml)

Русская версия по умолчанию. English version: [README_EN.md](README_EN.md).

Telegram-бот для продажи цифровых товаров: виртуальная валюта, аккаунты, Telegram Stars и другие позиции каталога. В проекте есть баланс пользователя, подтверждение покупки, выдача товара, админ-панель, интеграции с провайдерами и Docker-развертывание.

## Возможности

- Главное меню Telegram-бота с каталогом, профилем, покупками, настройками, информацией и поддержкой.
- Пополнение баланса через Platega и ссылки перевода LOLZ Balance.
- Интеграция LOLZ/LZT Market через официальный пакет `LOLZTEAM`.
- Подтверждение перед покупкой, чтобы пользователь явно видел сумму и товар.
- Зашифрованные снимки выдачи инвентаря.
- Админ-панель, экспорт пользователей, метрики, PostgreSQL backups, Prometheus и Grafana.
- Локализация на русском, английском и украинском языках.

## Стек

- Python 3.12+
- aiogram 3
- SQLAlchemy 2, Alembic, PostgreSQL, PgBouncer
- Redis
- Flask Admin
- uv
- Docker Compose

## Быстрый старт

Создай локальный `.env`:

```bash
cp .env.example .env
```

Минимально заполни:

```env
BOT_TOKEN="telegram-bot-token"
INVENTORY_ENCRYPTION_KEY="long-random-secret"
DB_PASS="strong-password"
SECRET_KEY="strong-admin-secret"
SECURITY_PASSWORD_SALT="strong-admin-salt"
```

Запусти сервисы:

```bash
docker compose up -d --build
```

Посмотреть логи бота:

```bash
docker compose logs -f bot
```

Применить миграции вручную:

```bash
docker compose run --rm migrator alembic upgrade head
```

## Разработка

Установка зависимостей:

```bash
uv sync --all-groups --dev
```

Проверки:

```bash
uv run pre-commit run --all-files
uv run ruff check bot tests admin
uv run ruff format --check bot tests admin
uv run pybabel compile -d bot/locales
uv run pytest
```

После изменения `.po` файлов компилируй переводы:

```bash
uv run pybabel compile -d bot/locales
```

## LOLZ / LZT

Бот использует `LOLZTEAM` для синхронизации маркет-инвентаря и проверки пополнений через LOLZ Balance.

Токен можно получить здесь:

- https://lzt.market/account/api
- https://lolz.live/account/api

Переменные:

```env
LOLZ_MARKET_ACCESS_TOKEN="token"
LOLZ_MARKET_BASE_URL="https://prod-api.lzt.market"
LOLZ_MARKET_CATEGORIES="telegram"
LOLZ_MARKET_SYNC_LIMIT_PER_CATEGORY=20
LOLZ_BALANCE_USERNAME="princeofscale"
LOLZ_BALANCE_CURRENCY="rub"
```

Синхронизация товаров:

```bash
docker compose exec bot python -m bot.scripts.sync_lolz_market
```

## Platega

Заполняй только если нужен прием платежей через Platega:

```env
PLATEGA_MERCHANT_ID="merchant-id"
PLATEGA_API_KEY="api-key"
PLATEGA_BASE_URL="https://app.platega.io"
PLATEGA_CALLBACK_PATH="/payments/platega/callback"
```

## Изображения

Картинки разделов лежат в `images/`:

- `menu.jpg` или `menu.png` для главного меню.
- `help.png` для помощи/поддержки.
- `profile.png` для профиля и баланса.
- `catalog.png`, `info.png`, `settings.png` для соответствующих разделов.
- `other.png` как fallback для остальных экранов.

## Безопасность

Политика безопасности и порядок сообщения об уязвимостях описаны в [SECURITY.md](SECURITY.md). Не создавай публичные GitHub issues для уязвимостей; используй GitHub Security Advisories.

## Репозиторий

- Не коммить `.env`: там реальные секреты.
- Коммить `.env.example`: он документирует форму конфигурации.
- CI запускает Ruff, pytest, Docker build, CodeQL, Hadolint и OpenSSF Scorecard.
- `main` защищен ruleset-ом: изменения должны проходить через PR и обязательные проверки.
- Автоматизация настроена для Dependabot, ImgBot, CodeRabbit, Mergify, Release Drafter и OpenSSF Scorecard.
