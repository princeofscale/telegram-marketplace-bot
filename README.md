# Telegram Marketplace Bot

Telegram bot for selling digital goods with a balance wallet, order delivery, admin tools, provider inventory sync, and Docker-based deployment.

## Features

- Telegram storefront with catalog, profile, purchases, settings, info, and support sections.
- Balance top-ups through Platega and LOLZ Balance transfer links.
- LOLZ/LZT Market integration through the official `LOLZTEAM` Python package.
- Purchase confirmation before charging user balance.
- Encrypted inventory delivery snapshots.
- Admin panel, user export, metrics, PostgreSQL backups, Prometheus, and Grafana.
- Localization for Russian, English, and Ukrainian.

## Stack

- Python 3.12+
- aiogram 3
- SQLAlchemy 2, Alembic, PostgreSQL, PgBouncer
- Redis
- Flask Admin
- uv
- Docker Compose

## Quick Start

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

```env
BOT_TOKEN="telegram-bot-token"
INVENTORY_ENCRYPTION_KEY="long-random-secret"
DB_PASS="strong-password"
SECRET_KEY="strong-admin-secret"
SECURITY_PASSWORD_SALT="strong-admin-salt"
```

Run the stack:

```bash
docker compose up -d --build
```

View logs:

```bash
docker compose logs -f bot
```

Run migrations manually when needed:

```bash
docker compose run --rm migrator alembic upgrade head
```

## Local Development

Install dependencies:

```bash
uv sync --all-groups --dev
```

Run checks:

```bash
uv run ruff check bot tests admin
uv run ruff format --check bot tests admin
uv run pytest
```

Compile translations after editing `.po` files:

```bash
uv run pybabel compile -d bot/locales
```

## LOLZ / LZT Setup

The bot uses `LOLZTEAM` for market inventory and LOLZ Balance payment verification.

Create a token at:

- https://lzt.market/account/api
- https://lolz.live/account/api

Set:

```env
LOLZ_MARKET_ACCESS_TOKEN="token"
LOLZ_MARKET_BASE_URL="https://prod-api.lzt.market"
LOLZ_MARKET_CATEGORIES="telegram"
LOLZ_MARKET_SYNC_LIMIT_PER_CATEGORY=20
LOLZ_BALANCE_USERNAME="princeofscale"
LOLZ_BALANCE_CURRENCY="rub"
```

Sync market items:

```bash
docker compose exec bot python -m bot.scripts.sync_lolz_market
```

## Platega Setup

Set these only if Platega payments should be enabled:

```env
PLATEGA_MERCHANT_ID="merchant-id"
PLATEGA_API_KEY="api-key"
PLATEGA_BASE_URL="https://app.platega.io"
PLATEGA_CALLBACK_PATH="/payments/platega/callback"
```

## Images

Section images live in `images/`:

- `menu.jpg` or `menu.png` for the main menu.
- `help.png` for support/help.
- `profile.png` for profile and wallet screens.
- `catalog.png`, `info.png`, `settings.png` for matching sections.
- `other.png` as fallback for sections without a dedicated image.

## Repository Notes

- Do not commit `.env`; it contains real secrets.
- Commit `.env.example`; it documents configuration shape with placeholders.
- Generated caches, bytecode, local backups, and virtual environments are ignored.
- CI runs Ruff and pytest on Python 3.13.
