# constants.py
"""
Константы проекта - все магические числа и строки в одном месте.
"""

# ============================================================================
# ВАЛИДАЦИЯ ПОЛЬЗОВАТЕЛЕЙ
# ============================================================================

# Никнейм
MIN_NICKNAME_LENGTH = 3
MAX_NICKNAME_LENGTH = 15
NICKNAME_PATTERN = r'^[a-zA-Z0-9_]{3,15}$'

# Username Telegram
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 32

# ============================================================================
# ВАЛИДАЦИЯ АККАУНТОВ (Capital.com)
# ============================================================================

MIN_API_KEY_LENGTH = 10
MIN_PASSWORD_LENGTH = 6
MIN_EMAIL_LENGTH = 3
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# ============================================================================
# ТОРГОВЛЯ
# ============================================================================

# Лимиты сделок (USDT)
MIN_TRADE_AMOUNT = 10.0
MAX_TRADE_AMOUNT = 100000.0

# Риск-менеджмент (проценты)
DEFAULT_STOP_LOSS_PERCENT = 5.0
DEFAULT_TAKE_PROFIT_PERCENT = 10.0
MAX_RISK_PER_TRADE_PERCENT = 100.0

# Валидные направления сделок
VALID_SIDES = {"LONG", "SHORT"}

# Валидные торговые пары
VALID_SYMBOLS = {"BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT"}

# ============================================================================
# РЕФЕРАЛЬНАЯ СИСТЕМА
# ============================================================================

# Cooldown для смены ника (дни)
NICKNAME_CHANGE_COOLDOWN_DAYS = 31

# ============================================================================
# API И ТАЙМАУТЫ
# ============================================================================

# Capital.com API
CAPITAL_BASE_URL = "https://demo-api-capital.backend-capital.com/api/v1"
CAPITAL_API_TIMEOUT_SECONDS = 10

# Forex pairs — Capital.com epics (used by market_data.py for market detection)
FOREX_PAIRS = [
    # Majors (7)
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "NZDUSD", "USDCAD",
    # Major crosses (21)
    "EURGBP", "EURJPY", "EURCHF", "EURAUD", "EURCAD", "EURNZD",
    "GBPJPY", "GBPCHF", "GBPAUD", "GBPCAD", "GBPNZD",
    "AUDJPY", "AUDNZD", "AUDCAD", "AUDCHF",
    "NZDJPY", "NZDCAD", "NZDCHF",
    "CADJPY", "CADCHF", "CHFJPY",
]

# ============================================================================
# ЯЗЫКИ
# ============================================================================

SUPPORTED_LANGUAGES = {"ru", "en", "ua"}
DEFAULT_LANGUAGE = "ru"

# ============================================================================
# FSM СОСТОЯНИЯ (чувствительные)
# ============================================================================

# Состояния, в которых ввод содержит секретные данные (пароли, API-ключи)
SENSITIVE_TRADING_STATES: set[str] = set()
