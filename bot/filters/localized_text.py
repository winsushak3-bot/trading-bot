# filters/localized_text.py
from typing import Callable, Union
from aiogram.filters import Filter
from aiogram.types import Message

class LocalizedText(Filter):
    def __init__(self, key: str):
        self.key = key

    async def __call__(self, message: Message, _: Callable) -> bool:
        # _ - это функция перевода, которая приходит из I18nMiddleware
        # Она уже знает текущий язык пользователя
        translated_text = _(self.key)
        return message.text == translated_text