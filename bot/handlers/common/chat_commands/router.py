# handlers/common/chat_commands/router.py
from aiogram import Router, F
from aiogram.types import Message
from shared.config import config

from .general.handlers import router as general_router
from .system.handlers import router as system_router

router = Router()

# ─── Allowed chats ────────────────────────────────────────────


def _is_allowed_chat(message: Message) -> bool:
    """Allow commands in main group topic."""
    cid = message.chat.id
    tid = message.message_thread_id
    if cid == config.CHANNEL_ID and tid == config.CHAT_TOPIC_ID:
        return True
    return False


# Системные команды могут работать в любой теме группы
system_router.message.filter(
    F.chat.id == config.CHANNEL_ID
)

# Остальные команды: main group (topic)
general_router.message.filter(_is_allowed_chat)

# Подключаем саб-роутеры к главному
router.include_routers(
    system_router,
    general_router,
)