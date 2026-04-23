# tests/unit/components/trading/test_validator.py
"""
Тесты для components/trading/validator.py
КРИТИЧНО! Защита от битых данных.
"""
import pytest
from shared.utils.validator import UserDataValidator


class TestUserDataValidator:
    """Тесты валидатора пользовательских данных."""
    
    @pytest.mark.parametrize("username,expected", [
        ("test_user", True),
        ("user123", True),
        ("Test_User_123", True),
        ("abc", True),  # Минимум 3 символа
        ("a" * 32, True),  # Максимум 32 символа
        (None, True),  # Username опциональный
        ("", True),
    ])
    def test_validate_username_valid(self, username, expected):
        """Тест: Валидные username."""
        is_valid, msg = UserDataValidator.validate_username(username)
        assert is_valid == expected
    
    @pytest.mark.parametrize("username,expected", [
        ("ab", False),
        ("a" * 33, False),
        ("user-name", False),
        ("user name", False),
        ("user@name", False),
    ])
    def test_validate_username_invalid(self, username, expected):
        """Тест: Невалидные username."""
        is_valid, msg = UserDataValidator.validate_username(username)
        assert is_valid == expected
    
    @pytest.mark.parametrize("nickname,expected", [
        ("Shadow", True),
        ("Trader007", True),
        ("User_123", True),
        ("abc", True),  # Минимум 3 символа
        ("a" * 15, True),  # Максимум 15 символов
        ("abcdefghij", True),  # 10 символов — валидно
        ("a" * 11, True),  # 11 символов — валидно (макс 15)
    ])
    def test_validate_nickname_valid(self, nickname, expected):
        """Тест: Валидные никнеймы."""
        is_valid, msg = UserDataValidator.validate_nickname(nickname)
        assert is_valid == expected
    
    @pytest.mark.parametrize("nickname,expected", [
        ("", False),
        ("a", False),  # Меньше 3 символов
        ("ab", False),  # Меньше 3 символов
        ("a" * 16, False),  # Больше 15 символов
        ("user name", False),  # С пробелом
        ("user@name", False),  # Спецсимвол
        ("Тест", False),  # Кириллица не допускается паттерном
        ("Test-User", False),  # Дефис не допускается паттерном
        (None, False),
        (123, False),
    ])
    def test_validate_nickname_invalid(self, nickname, expected):
        """Тест: Невалидные никнеймы."""
        is_valid, msg = UserDataValidator.validate_nickname(nickname)
        assert is_valid == expected
    
    @pytest.mark.parametrize("language,expected", [
        ("ru", True),
        ("en", True),
        ("ua", True),
        ("RU", True),  # Uppercase
        (" ru ", True),  # С пробелами
    ])
    def test_validate_language_valid(self, language, expected):
        """Тест: Валидные языки."""
        is_valid, msg = UserDataValidator.validate_language(language)
        assert is_valid == expected
    
    @pytest.mark.parametrize("language,expected", [
        ("", False),
        ("fr", False),  # Неподдерживаемый
        ("rus", False),
        (None, False),
        (123, False),
    ])
    def test_validate_language_invalid(self, language, expected):
        """Тест: Невалидные языки."""
        is_valid, msg = UserDataValidator.validate_language(language)
        assert is_valid == expected


class TestValidatorEdgeCases:
    """Тесты граничных случаев и защиты от инъекций."""
    
    def test_xss_in_nickname(self):
        """Тест: XSS в никнейме."""
        is_valid, msg = UserDataValidator.validate_nickname("<script>alert('xss')</script>")
        assert is_valid is False
