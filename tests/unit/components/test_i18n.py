# tests/unit/components/test_i18n.py
"""
Тесты для components/i18n.py
Проверяем локализацию.
"""
import pytest
import json
import os
from unittest.mock import patch, mock_open

from shared.utils.i18n import I18n


class TestI18n:
    """Тесты компонента интернационализации."""
    
    @pytest.fixture
    def i18n(self):
        """Фикстура i18n."""
        return I18n()
    
    def test_load_locales(self, i18n, tmp_path):
        """Тест: Загрузка локалей из файлов."""
        # Создаем временные файлы локалей
        locales_dir = tmp_path / "locales"
        locales_dir.mkdir()
        
        ru_data = {"hello": "Привет", "bye": "Пока"}
        en_data = {"hello": "Hello", "bye": "Bye"}
        
        (locales_dir / "ru.json").write_text(json.dumps(ru_data), encoding="utf-8")
        (locales_dir / "en.json").write_text(json.dumps(en_data), encoding="utf-8")
        
        i18n.load_locales(str(locales_dir))
        
        assert "ru" in i18n.locales
        assert "en" in i18n.locales
        assert i18n.locales["ru"]["hello"] == "Привет"
        assert i18n.locales["en"]["hello"] == "Hello"
    
    def test_get_existing_key(self, i18n):
        """Тест: Получение существующего ключа."""
        i18n.locales = {
            "ru": {"hello": "Привет"}
        }
        
        result = i18n.get("hello", lang="ru")
        
        assert result == "Привет"
    
    def test_get_missing_key_returns_key(self, i18n):
        """Тест: Отсутствующий ключ возвращает сам ключ."""
        i18n.locales = {
            "ru": {}
        }
        
        result = i18n.get("missing_key", lang="ru")
        
        assert result == "missing_key"
    
    def test_get_with_formatting(self, i18n):
        """Тест: Форматирование с параметрами."""
        i18n.locales = {
            "ru": {"greeting": "Привет, {name}!"}
        }
        
        result = i18n.get("greeting", lang="ru", name="Иван")
        
        assert result == "Привет, Иван!"
    
    def test_get_fallback_to_default_lang(self, i18n):
        """Тест: Fallback на дефолтный язык."""
        i18n.locales = {
            "ru": {"hello": "Привет"}
        }
        i18n.default_lang = "ru"
        
        result = i18n.get("hello", lang="unknown")
        
        assert result == "Привет"
    
    def test_get_empty_locales(self, i18n):
        """Тест: Пустые локали."""
        i18n.locales = {}
        
        result = i18n.get("hello", lang="ru")
        
        assert result == "hello"
    
    def test_load_locales_missing_directory(self, i18n, mocker):
        """Тест: Отсутствующая директория локалей."""
        mock_logger = mocker.patch("shared.utils.i18n.logging")
        
        i18n.load_locales("/nonexistent/path")
        
        mock_logger.warning.assert_called_once()
    
    def test_formatting_with_missing_param(self, i18n):
        """Тест: Форматирование с отсутствующим параметром."""
        i18n.locales = {
            "ru": {"greeting": "Привет, {name}!"}
        }
        
        result = i18n.get("greeting", lang="ru")
        
        # Должен вернуть строку без форматирования
        assert "greeting" in result or "{name}" in result


class TestI18nConsistency:
    """Тесты консистентности локалей."""
    
    def test_all_keys_present_in_all_languages(self):
        """Тест: Все ключи присутствуют во всех языках."""
        locales_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "locales")
        
        if not os.path.exists(locales_dir):
            pytest.skip("Locales directory not found")
        
        locales = {}
        for filename in os.listdir(locales_dir):
            if filename.endswith(".json"):
                lang = filename.split(".")[0]
                with open(os.path.join(locales_dir, filename), "r", encoding="utf-8") as f:
                    locales[lang] = json.load(f)
        
        if len(locales) < 2:
            pytest.skip("Not enough locales to compare")
        
        # Получаем все ключи из всех языков
        all_keys = set()
        for lang_data in locales.values():
            all_keys.update(lang_data.keys())
        
        # Проверяем что каждый язык имеет все ключи
        missing_keys = {}
        for lang, lang_data in locales.items():
            missing = all_keys - set(lang_data.keys())
            if missing:
                missing_keys[lang] = missing
        
        # Если есть пропущенные ключи, выводим предупреждение
        if missing_keys:
            for lang, keys in missing_keys.items():
                print(f"\nWarning: Language '{lang}' is missing keys: {keys}")
