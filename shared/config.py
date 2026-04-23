# config.py

# IMPORTS

from typing import List, Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, field_validator

# SETTINGS CLASS

class Settings(BaseSettings):
    # TELEGRAM
    BOT_TOKEN: SecretStr
    ADMIN_IDS: List[int]
    ADMIN_PASSWORD: Optional[SecretStr] = None  # Пароль для логина в /admin UI (когда открывается из браузера, не из Telegram WebApp)
    CHANNEL_ID: int
    CHAT_TOPIC_ID: Optional[int] = None

    # DATABASE AND REDIS
    DB_URL: str
    REDIS_URL: str

    # TRADING
    TRADING_MODE: Literal["DEMO", "REAL"] = "DEMO"
    
    # CAPITAL.COM
    CAPITAL_EMAIL: str
    CAPITAL_PASSWORD: SecretStr
    CAPITAL_API_KEY: SecretStr

    # BYBIT
    BYBIT_API_KEY: Optional[SecretStr] = None
    BYBIT_SECRET: Optional[SecretStr] = None

    # WEB
    WEBAPP_BASE_URL: Optional[str] = None

    # SECURITY
    ENCRYPTION_KEY: SecretStr
    WEBHOOK_BASE_URL: Optional[str] = None

    # ── VALIDATORS ──────────────────────────────────────────────
    #
    # Единая точка валидации для секретов/URL, чтобы не разбрасывать
    # проверки по `bot/main.py`, `backend/main.py`
    # и т.д. — и не иметь «длина ≥ 32», которая ничего не гарантирует
    # для Fernet.

    @field_validator("ADMIN_PASSWORD")
    @classmethod
    def _validate_admin_password(cls, v: Optional[SecretStr]) -> Optional[SecretStr]:
        """ADMIN_PASSWORD должен быть минимум 8 символов если задан."""
        if v is None:
            return v
        raw = v.get_secret_value() if isinstance(v, SecretStr) else v
        if raw and len(raw) < 8:
            raise ValueError(
                "ADMIN_PASSWORD слишком короткий (минимум 8 символов). "
                "Текущий пароль небезопасен."
            )
        return v

    @field_validator("ENCRYPTION_KEY")
    @classmethod
    def _validate_fernet_key(cls, v: SecretStr) -> SecretStr:
        """ENCRYPTION_KEY должен быть валидным Fernet-ключом (44-символьный
        url-safe base64, кодирующий 32 байта). Сгенерировать можно так:

            python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
        """
        # Импорт внутри — чтобы `shared.config` не тянул cryptography, если
        # её случайно нет в окружении (например, в урезанных утилитах).
        from cryptography.fernet import Fernet

        raw = v.get_secret_value() if isinstance(v, SecretStr) else v
        if not raw:
            raise ValueError("ENCRYPTION_KEY не может быть пустым")
        try:
            Fernet(raw.encode())
        except Exception as e:
            raise ValueError(
                "ENCRYPTION_KEY должен быть валидным Fernet-ключом "
                "(44-символьный url-safe base64). "
                "Сгенерируйте новый:\n"
                "  python -c \"from cryptography.fernet import Fernet; "
                "print(Fernet.generate_key().decode())\"\n"
                f"Детали ошибки: {e}"
            ) from e
        return v

    @field_validator("DB_URL")
    @classmethod
    def _validate_db_url(cls, v: str) -> str:
        """DB_URL должен использовать известный нам диалект + async-драйвер."""
        if not v:
            raise ValueError("DB_URL не может быть пустым")
        # Допускаем postgresql+asyncpg, sqlite+aiosqlite и варианты без драйвера.
        if not v.startswith(("postgresql", "sqlite")):
            raise ValueError(
                f"DB_URL должен начинаться с postgresql:// или sqlite:// (получено: {v[:20]}...)"
            )
        return v

    @field_validator("REDIS_URL")
    @classmethod
    def _validate_redis_url(cls, v: str) -> str:
        """REDIS_URL допускает redis:// (plain) и rediss:// (TLS)."""
        if not v:
            raise ValueError("REDIS_URL не может быть пустым")
        if not v.startswith(("redis://", "rediss://")):
            raise ValueError(
                f"REDIS_URL должен начинаться с redis:// или rediss:// (получено: {v[:20]}...)"
            )
        return v

    # PYDANTIC CONFIG
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# GLOBAL CONFIG INSTANCE

config = Settings()