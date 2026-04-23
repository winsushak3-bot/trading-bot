# database/models/accounts.py

from sqlalchemy import BigInteger, String, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class BrokerAccount(Base):
    __tablename__ = "broker_accounts"

    # Запрещаем создавать аккаунты с одинаковым именем для одного юзера
    __table_args__ = (
        UniqueConstraint("user_id", "account_name", name="uq_user_account_name"),
        # Составной индекс для частого запроса: get_account(user_id, broker)
        Index("ix_user_broker", "user_id", "broker_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Связь с юзером
    user_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey("users.tg_id", ondelete="CASCADE"), 
        index=True
    )

    # Тип брокера (пока только Capital, но задел на будущее для Bybit)
    broker_name: Mapped[str] = mapped_column(String(20), default="capital")
    
    # Название аккаунта (для удобства, если будет мультиаккаунт)
    account_name: Mapped[str] = mapped_column(String(255), default="Demo Account")

    # 🔥 ЗАШИФРОВАННЫЕ ДАННЫЕ
    # Мы храним их как строки, но внутри там "каша" из символов
    api_key_enc: Mapped[str] = mapped_column(String(500))
    password_enc: Mapped[str] = mapped_column(String(500)) # Пароль от аккаунта Capital
    
    # Флаг демо (на будущее, если решишь добавить Реал)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Флаг валидности (если ключи протухли, ставим False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<BrokerAccount(id={self.id}, user_id={self.user_id}, broker='{self.broker_name}', account='{self.account_name}')>"