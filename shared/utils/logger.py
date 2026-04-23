# utils/logger.py

import logging
import sys

from loguru import logger


class _InterceptHandler(logging.Handler):
    """
    Перехватывает записи stdlib logging и перенаправляет в loguru.

    Благодаря этому backend (FastAPI) и внешние библиотеки, использующие
    `logging.getLogger(__name__)`, логируются в том же формате/файле, что и
    код, работающий через `from loguru import logger`.
    """

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - passthrough
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


_CONFIGURED = False


def setup_logger(level: str = "INFO"):
    """Настройка единого логгера проекта (loguru + bridge stdlib logging)."""
    global _CONFIGURED

    if _CONFIGURED:
        return logger

    logger.remove()

    # Лог в консоль
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
    )

    # Лог в файл
    logger.add(
        "logs/bot.log",
        rotation="10 MB",
        retention="1 week",
        level="WARNING",
        compression="zip",
    )

    # Bridge stdlib logging → loguru (единый вывод для всех зависимостей)
    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi", "aiogram", "aiohttp"):
        lg = logging.getLogger(name)
        lg.handlers = [_InterceptHandler()]
        lg.propagate = False

    _CONFIGURED = True
    return logger