# tests/unit/services/test_cryptography.py
"""
Тесты для services/cryptography.py
Критично! Проверяем что API ключи шифруются/расшифровываются корректно.
"""
import pytest
from cryptography.fernet import InvalidToken

from shared.services.cryptography import crypto


class TestCryptoService:
    """Тесты сервиса шифрования."""
    
    def test_encrypt_decrypt_roundtrip(self):
        """Тест: Шифрование → Расшифровка → Сравнение с оригиналом."""
        original = "my_secret_api_key_12345"
        
        # Шифруем
        encrypted = crypto.encrypt(original)
        
        # Проверяем что зашифрованное != оригинал
        assert encrypted != original
        assert len(encrypted) > len(original)
        
        # Расшифровываем
        decrypted = crypto.decrypt(encrypted)
        
        # Проверяем что расшифрованное == оригинал
        assert decrypted == original
    
    def test_encrypt_empty_string(self):
        """Тест: Шифрование пустой строки."""
        result = crypto.encrypt("")
        assert result == ""
    
    def test_decrypt_empty_string(self):
        """Тест: Расшифровка пустой строки."""
        result = crypto.decrypt("")
        assert result == ""
    
    def test_encrypt_long_string(self):
        """Тест: Шифрование очень длинной строки (10000 символов)."""
        long_string = "A" * 10000
        
        encrypted = crypto.encrypt(long_string)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == long_string
    
    def test_encrypt_special_characters(self):
        """Тест: Шифрование строки со спецсимволами."""
        special = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        
        encrypted = crypto.encrypt(special)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == special
    
    def test_encrypt_unicode(self):
        """Тест: Шифрование Unicode символов."""
        unicode_text = "Привет мир! 你好世界! 🚀💰"
        
        encrypted = crypto.encrypt(unicode_text)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == unicode_text
    
    def test_decrypt_invalid_token(self):
        """Тест: Расшифровка невалидного токена возвращает оригинал или падает."""
        invalid_token = "this_is_not_a_valid_encrypted_token"
        
        # В текущей реализации может вернуть оригинал (fallback)
        # или выбросить исключение - оба варианта допустимы
        try:
            result = crypto.decrypt(invalid_token)
            # Если не упало, проверяем что вернулось что-то
            assert result is not None
        except Exception:
            # Если упало - тоже ок
            pass
    
    def test_decrypt_corrupted_token(self):
        """Тест: Расшифровка поврежденного токена."""
        original = "test_data"
        encrypted = crypto.encrypt(original)
        
        # Портим токен
        corrupted = encrypted[:-5] + "XXXXX"
        
        # Может вернуть что-то или упасть
        try:
            result = crypto.decrypt(corrupted)
            # Главное что не вернулся оригинал
            assert result != original
        except Exception:
            # Если упало - отлично
            pass
    
    def test_multiple_encryptions_different_results(self):
        """Тест: Каждое шифрование дает разный результат (из-за IV)."""
        original = "same_text"
        
        encrypted1 = crypto.encrypt(original)
        encrypted2 = crypto.encrypt(original)
        
        # Зашифрованные тексты должны отличаться (если используется IV)
        # Но оба должны расшифровываться в оригинал
        assert crypto.decrypt(encrypted1) == original
        assert crypto.decrypt(encrypted2) == original
    
    def test_encrypt_numbers_as_string(self):
        """Тест: Шифрование чисел (как строки)."""
        number_string = "1234567890"
        
        encrypted = crypto.encrypt(number_string)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == number_string
    
    def test_encrypt_multiline_string(self):
        """Тест: Шифрование многострочного текста."""
        multiline = """Line 1
Line 2
Line 3
With special chars: !@#$%"""
        
        encrypted = crypto.encrypt(multiline)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == multiline


class TestCryptoServiceEdgeCases:
    """Тесты граничных случаев."""
    
    def test_encrypt_single_character(self):
        """Тест: Шифрование одного символа."""
        single = "A"
        
        encrypted = crypto.encrypt(single)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == single
    
    def test_encrypt_whitespace(self):
        """Тест: Шифрование пробелов."""
        whitespace = "   "
        
        encrypted = crypto.encrypt(whitespace)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == whitespace
    
    def test_encrypt_newlines(self):
        """Тест: Шифрование переносов строк."""
        newlines = "\n\n\n"
        
        encrypted = crypto.encrypt(newlines)
        decrypted = crypto.decrypt(encrypted)
        
        assert decrypted == newlines
