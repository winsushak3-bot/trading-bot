# components/trading/validator.py
"""
Компонент валидации пользовательских данных.
"""
import re
from typing import Tuple
from shared.constants import (
    MIN_USERNAME_LENGTH, MAX_USERNAME_LENGTH,
    MIN_NICKNAME_LENGTH, MAX_NICKNAME_LENGTH, NICKNAME_PATTERN,
    SUPPORTED_LANGUAGES
)


class UserDataValidator:
    """Валидатор пользовательских данных."""
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """Проверяет имя пользователя Telegram."""
        if not username or not isinstance(username, str):
            return True, ""  # Username опциональный
        
        if len(username) < MIN_USERNAME_LENGTH:
            return False, f"Username должен быть минимум {MIN_USERNAME_LENGTH} символа"
        
        if len(username) > MAX_USERNAME_LENGTH:
            return False, f"Username не должен быть больше {MAX_USERNAME_LENGTH} символов"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username может содержать только буквы, цифры и подчеркивание"
        
        return True, ""
    
    @staticmethod
    def validate_nickname(nickname: str) -> Tuple[bool, str]:
        """Проверяет пользовательский ник."""
        if not nickname or not isinstance(nickname, str):
            return False, "Ник должен быть строкой"
        
        nickname = nickname.strip()
        
        if len(nickname) < MIN_NICKNAME_LENGTH:
            return False, f"Ник должен быть минимум {MIN_NICKNAME_LENGTH} символа"
        
        if len(nickname) > MAX_NICKNAME_LENGTH:
            return False, f"Ник не должен быть больше {MAX_NICKNAME_LENGTH} символов"
        
        if not re.match(NICKNAME_PATTERN, nickname):
            return False, "Ник может содержать только латинские буквы, цифры и подчеркивание"
        
        return True, ""
    
    @staticmethod
    def validate_language(language: str) -> Tuple[bool, str]:
        """Проверяет код языка."""
        if not language or not isinstance(language, str):
            return False, "Язык должен быть строкой"
        
        language_lower = language.lower().strip()
        
        if language_lower not in SUPPORTED_LANGUAGES:
            return False, f"Поддерживаемые языки: {', '.join(SUPPORTED_LANGUAGES)}"
        
        return True, ""
