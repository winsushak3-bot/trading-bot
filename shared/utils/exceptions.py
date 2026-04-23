# utils/exceptions.py
"""
Кастомные исключения для проекта бота.
"""


class BotException(Exception):
    """Базовое исключение для всех ошибок бота."""
    pass


class CapitalApiException(BotException):
    """Исключение при работе с Capital.com API."""
    pass


class CapitalAuthException(CapitalApiException):
    """Ошибка аутентификации на Capital.com."""
    pass


class DatabaseException(BotException):
    """Исключение при работе с базой данных."""
    pass


class ValidationException(BotException):
    """Ошибка валидации данных."""
    pass
