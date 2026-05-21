from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic_settings import BaseSettings, SettingsConfigDict

from bot.modules.admins.policy import parse_admin_user_ids

if TYPE_CHECKING:
    from sqlalchemy.engine.url import URL

DIR = Path(__file__).absolute().parent.parent.parent
BOT_DIR = Path(__file__).absolute().parent.parent
LOCALES_DIR = f"{BOT_DIR}/locales"
I18N_DOMAIN = "messages"
DEFAULT_LOCALE = "en"


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class WebhookSettings(EnvBaseSettings):
    USE_WEBHOOK: bool = False
    WEBHOOK_BASE_URL: str = "https://xxx.ngrok-free.app"
    WEBHOOK_PATH: str = "/webhook"
    WEBHOOK_SECRET: str = ""
    WEBHOOK_HOST: str = "localhost"
    WEBHOOK_PORT: int = 8080

    @property
    def webhook_url(self) -> str:
        if settings.USE_WEBHOOK:
            return f"{self.WEBHOOK_BASE_URL}{self.WEBHOOK_PATH}"
        return f"http://localhost:{settings.WEBHOOK_PORT}{settings.WEBHOOK_PATH}"


class BotSettings(WebhookSettings):
    BOT_TOKEN: str
    SUPPORT_URL: str | None = None
    RATE_LIMIT: int | float = 0.5  # for throttling control
    INVENTORY_ENCRYPTION_KEY: str
    BOT_PUBLIC_URL: str = "https://t.me/VoxMarketBot"
    DEFAULT_ADMIN_USER_IDS: str = "1314697368"

    @property
    def default_admin_user_ids(self) -> frozenset[int]:
        return parse_admin_user_ids(self.DEFAULT_ADMIN_USER_IDS)


class PlategaSettings(EnvBaseSettings):
    PLATEGA_MERCHANT_ID: str | None = None
    PLATEGA_API_KEY: str | None = None
    PLATEGA_BASE_URL: str = "https://app.platega.io"
    PLATEGA_CALLBACK_PATH: str = "/payments/platega/callback"


class LolzMarketSettings(EnvBaseSettings):
    LOLZ_MARKET_ACCESS_TOKEN: str | None = None
    LOLZ_MARKET_BASE_URL: str = "https://prod-api.lzt.market"
    LOLZ_MARKET_CATEGORIES: str = "telegram"
    LOLZ_MARKET_SYNC_LIMIT_PER_CATEGORY: int = 20
    LOLZ_BALANCE_USERNAME: str = "princeofscale"
    LOLZ_BALANCE_CURRENCY: str = "rub"

    @property
    def lolz_market_categories(self) -> tuple[str, ...]:
        return tuple(category.strip() for category in self.LOLZ_MARKET_CATEGORIES.split(",") if category.strip())


class DBSettings(EnvBaseSettings):
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASS: str | None = None
    DB_NAME: str = "postgres"

    @property
    def database_url(self) -> URL | str:
        if self.DB_PASS:
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return f"postgresql+asyncpg://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def database_url_psycopg2(self) -> str:
        if self.DB_PASS:
            return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return f"postgresql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class CacheSettings(EnvBaseSettings):
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASS: str | None = None

    # REDIS_DATABASE: int = 1
    # REDIS_USERNAME: int | None = None
    # REDIS_TTL_STATE: int | None = None
    # REDIS_TTL_DATA: int | None = None

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASS:
            return f"redis://{self.REDIS_PASS}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"


class Settings(BotSettings, DBSettings, CacheSettings, PlategaSettings, LolzMarketSettings):
    DEBUG: bool = False

    SENTRY_DSN: str | None = None

    AMPLITUDE_API_KEY: str  # or for example it could be POSTHOG_API_KEY


settings = Settings()
