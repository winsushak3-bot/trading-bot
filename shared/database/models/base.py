# database/models/base.py

from datetime import datetime
from sqlalchemy import DateTime, JSON, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Cross-dialect JSON: на PostgreSQL — нативный JSONB (с индексами),
# на SQLite/остальных — обычный JSON (важно для тестов и локальной разработки).
JsonType = JSON().with_variant(JSONB(), "postgresql")

class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    
    # Автоматически добавляем время создания записи
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Автоматически обновляем время при изменении записи
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        server_onupdate=func.now()
    )

    def __repr__(self):
        """Красивый вывод модели при принте."""
        cols = []
        for col in self.__table__.columns.keys():
            cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__} {', '.join(cols)}>"