# handlers/common/chat_commands/system/handlers.py
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("topic"))
async def get_topic_id(message: types.Message):
    """Служебная команда для узнавания ID текущего топика"""
    if message.message_thread_id:
        await message.answer(f"ID этой темы: <code>{message.message_thread_id}</code>")
    else:
        await message.answer(f"Это основная ветка группы. ID группы: <code>{message.chat.id}</code>")