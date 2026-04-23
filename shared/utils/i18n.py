# components/i18n.py
import json
import logging
import os
from typing import Dict

class I18n:
    def __init__(self):
        self.locales: Dict[str, Dict[str, str]] = {}
        self.default_lang = "ru"

    def load_locales(self, locales_dir: str | None = None):
        """Загружает все .json файлы из папки locales.

        По умолчанию ищет папку locales рядом с корнем проекта,
        независимо от того, из какой директории запущен скрипт.
        """
        if locales_dir is None:
            # Путь <project_root>/locales
            project_root = os.path.dirname(os.path.dirname(__file__))
            locales_dir = os.path.join(project_root, "locales")

        # Проверка, чтобы не падало, если папки нет
        if not os.path.exists(locales_dir):
            logging.warning(f"⚠️ Папка {locales_dir} не найдена. Пропускаем загрузку.")
            return

        for filename in os.listdir(locales_dir):
            if filename.endswith(".json"):
                # Защита от path traversal
                if ".." in filename or "/" in filename or "\\" in filename:
                    logging.warning(f"⚠️ Подозрительное имя файла: {filename}. Пропускаем.")
                    continue
                
                lang_code = filename.split(".")[0]  # ru.json -> ru
                filepath = os.path.join(locales_dir, filename)
                
                # Дополнительная проверка: файл должен быть внутри locales_dir
                if not os.path.abspath(filepath).startswith(os.path.abspath(locales_dir)):
                    logging.warning(f"⚠️ Попытка выхода за пределы папки: {filename}")
                    continue
                
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        self.locales[lang_code] = json.load(f)
                        logging.info(f"✅ Локаль загружена: {lang_code}")
                except Exception as e:
                    logging.error(f"❌ Ошибка загрузки локали {filename}: {e}")

    def get(self, key: str, lang: str = "ru", **kwargs) -> str:
        """Возвращает текст по ключу."""
        lang_data = self.locales.get(lang, self.locales.get(self.default_lang, {}))
        text = lang_data.get(key, key)
        
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError):
                return text
        return text

# Создаем один экземпляр на весь проект
i18n = I18n()