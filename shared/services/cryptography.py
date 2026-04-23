# services/cryptography.py
from cryptography.fernet import Fernet, InvalidToken
import logging

logger = logging.getLogger(__name__)


class CryptoService:
    def __init__(self):
        """Инициализируем шифр.

        Использует ENCRYPTION_KEY как валидный Fernet-ключ (base64).
        Импорт конфига выполняется здесь (не на уровне модуля), чтобы
        модуль можно было импортировать без побочных эффектов
        (важно для тестов и инструментов, не нуждающихся в шифровании).
        """
        # Ленивая загрузка конфига — только при фактической инициализации.
        from shared.config import config

        raw = config.ENCRYPTION_KEY.get_secret_value()

        try:
            self.cipher = Fernet(raw.encode())
            logger.info("CryptoService: using Fernet key from config")
        except Exception as e:
            logger.exception("Failed to initialize Fernet cipher: %s", e)
            raise ValueError(f"Invalid ENCRYPTION_KEY format. Must be valid Fernet key (base64): {e}")

    def encrypt(self, text: str) -> str:
        """Шифрует строку. Пустые строки возвращаются пустыми."""
        if not text:
            return ""
        return self.cipher.encrypt(text.encode()).decode()

    def decrypt(self, token: str) -> str:
        """Расшифровывает строку.
        
        Raises:
            InvalidToken: Если не удалось расшифровать
        """
        if not token:
            return ""

        try:
            return self.cipher.decrypt(token.encode()).decode()
        except InvalidToken as e:
            logger.error(f"Failed to decrypt token: {e}")
            raise


# ── Ленивый singleton через PEP 562 module-level __getattr__ ──
#
# Раньше здесь было `crypto = CryptoService()`, что заставляло
# `ENCRYPTION_KEY` быть валидным Fernet-ключом на момент ИМПОРТА модуля.
# Это ломало тесты и любые CLI-инструменты, не использующие шифрование.
#
# Теперь `crypto` создаётся при первом обращении:
#     from shared.services.cryptography import crypto
#     crypto.encrypt("...")  # <- вот здесь инициализируется
#
# Обратная совместимость сохранена: существующие `from ... import crypto`
# продолжают работать без изменений.

_crypto_singleton: "CryptoService | None" = None


def _get_crypto() -> CryptoService:
    global _crypto_singleton
    if _crypto_singleton is None:
        _crypto_singleton = CryptoService()
    return _crypto_singleton


def __getattr__(name: str):
    if name == "crypto":
        return _get_crypto()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def reset_crypto_for_tests() -> None:
    """Сбрасывает singleton — только для тестов, когда нужно переинициализировать
    сервис с новым ENCRYPTION_KEY (например, после подмены конфига)."""
    global _crypto_singleton
    _crypto_singleton = None