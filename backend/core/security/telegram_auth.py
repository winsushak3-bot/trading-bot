import hmac
import hashlib
import json
import logging
import time
from urllib.parse import parse_qs
from typing import Optional

from shared.config import config

logger = logging.getLogger(__name__)

# Максимальный возраст Telegram initData (секунды).
# Telegram рекомендует отклонять initData старше 24 часов.
INIT_DATA_MAX_AGE_SECONDS = 86400


def validate_telegram_init_data(init_data: str) -> Optional[dict]:
    """
    Валидирует initData от Telegram WebApp.
    Возвращает данные пользователя или None.

    Проверки:
    1. HMAC hash (подпись Telegram через BOT_TOKEN).
    2. auth_date не старше INIT_DATA_MAX_AGE_SECONDS.
    """
    try:
        # Парсим данные
        parsed = parse_qs(init_data)

        # Получаем hash
        received_hash = parsed.get('hash', [None])[0]
        if not received_hash:
            return None

        # Удаляем hash из данных
        data_check_string_parts = []
        for key in sorted(parsed.keys()):
            if key != 'hash':
                value = parsed[key][0]
                data_check_string_parts.append(f"{key}={value}")

        data_check_string = '\n'.join(data_check_string_parts)

        # Создаем secret key
        bot_token = config.BOT_TOKEN.get_secret_value()
        secret_key = hmac.new(
            "WebAppData".encode(),
            bot_token.encode(),
            hashlib.sha256
        ).digest()

        # Вычисляем hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        # Проверяем hash (используем compare_digest для защиты от timing-атак)
        if not hmac.compare_digest(calculated_hash, received_hash):
            return None

        # Проверяем возраст initData
        auth_date_str = parsed.get('auth_date', [None])[0]
        if not auth_date_str:
            logger.warning("Telegram initData missing auth_date")
            return None
        try:
            auth_date = int(auth_date_str)
        except ValueError:
            logger.warning(f"Telegram initData invalid auth_date: {auth_date_str}")
            return None

        age = int(time.time()) - auth_date
        if age > INIT_DATA_MAX_AGE_SECONDS:
            logger.warning(f"Telegram initData expired: age={age}s")
            return None
        if age < -300:  # небольшой допуск на рассинхрон часов (5 минут)
            logger.warning(f"Telegram initData from future: age={age}s")
            return None

        # Парсим данные пользователя
        user_data = parsed.get('user', [None])[0]
        if user_data:
            return json.loads(user_data)

        return None

    except Exception as e:
        logger.error(f"Telegram auth error: {e}")
        return None
