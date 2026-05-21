# Telegram Marketplace Bot

![CodeRabbit Pull Request Reviews](https://img.shields.io/coderabbit/prs/github/princeofscale/telegram-marketplace-bot?utm_source=oss&utm_medium=github&utm_campaign=princeofscale%2Ftelegram-marketplace-bot&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews)
[![Linting](https://github.com/princeofscale/telegram-marketplace-bot/actions/workflows/linters.yml/badge.svg)](https://github.com/princeofscale/telegram-marketplace-bot/actions/workflows/linters.yml)
[![CodeQL](https://github.com/princeofscale/telegram-marketplace-bot/actions/workflows/codeql.yml/badge.svg)](https://github.com/princeofscale/telegram-marketplace-bot/actions/workflows/codeql.yml)
[![OpenSSF Scorecard](https://github.com/princeofscale/telegram-marketplace-bot/actions/workflows/scorecard.yml/badge.svg)](https://github.com/princeofscale/telegram-marketplace-bot/actions/workflows/scorecard.yml)

Russian is the default README language. Русская версия: [README.md](README.md).

Telegram bot for selling digital goods: virtual currency, accounts, Telegram Stars, and other catalog items. The project includes user balance, purchase confirmation, item delivery, admin tooling, provider integrations, and Docker-based deployment.

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

Create a local `.env`:

```bash
cp .env.example .env
```

Set at minimum:

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

View bot logs:

```bash
docker compose logs -f bot
```

Run migrations manually:

```bash
docker compose run --rm migrator alembic upgrade head
```

## Development

Install dependencies:

```bash
uv sync --all-groups --dev
```

Run checks:

```bash
uv run pre-commit run --all-files
uv run ruff check bot tests admin
uv run ruff format --check bot tests admin
uv run pybabel compile -d bot/locales
uv run pytest
```

Compile translations after editing `.po` files:

```bash
uv run pybabel compile -d bot/locales
```

## LOLZ / LZT

The bot uses `LOLZTEAM` for market inventory sync and LOLZ Balance payment verification.

Create a token at:

- https://lzt.market/account/api
- https://lolz.live/account/api

Configuration:

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

## Platega

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

## Security

Security policy and vulnerability reporting instructions are documented in [SECURITY.md](SECURITY.md). Do not open public GitHub issues for security problems; use GitHub Security Advisories instead.

## Repository

- Do not commit `.env`; it contains real secrets.
- Commit `.env.example`; it documents the configuration shape.
- CI runs Ruff, pytest, Docker build, CodeQL, Hadolint, and OpenSSF Scorecard.
- `main` is protected by a ruleset: changes must go through PRs and required checks.
- Repository automation is configured for Dependabot, ImgBot, CodeRabbit, Mergify, Release Drafter, and OpenSSF Scorecard.
