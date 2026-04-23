# handlers/common/chat_commands/general/handlers.py
from aiogram import Router, types
from aiogram.filters import Command
from typing import Callable

router = Router()

@router.message(Command("help", "menu", "command"))
async def show_chat_commands(message: types.Message, _: Callable):
    """Показывает список доступных команд"""
    await message.answer(_("chat_commands_text"))