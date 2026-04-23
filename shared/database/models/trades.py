# database/models/trades.py

from sqlalchemy import ForeignKey, String, Float, Integer, BigInteger, Index
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Trade(Base):
    __tablename__ = "trades"
    
    __table_args__ = (
        # Составной индекс для частого запроса: поиск сделок по user_id и status
        Index("ix_user_status", "user_id", "status"),
        # Сортировка «последние сделки»
        Index("ix_trades_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Ссылка на пользователя (владелец)
    user_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey("users.tg_id", ondelete="CASCADE")
    )

    # Ссылка на конкретный брокерский аккаунт (чтобы различать Demo/Real/Subaccounts)
    #
    # ondelete="SET NULL" — при удалении брокерского аккаунта мы хотим СОХРАНИТЬ
    # историю сделок для аналитики/PnL-графиков, просто «отвязав» их от аккаунта.
    # Ранее был CASCADE, что стирало всю историю сделок пользователя одним
    # кликом «Отключить брокера» — неприемлемо для финансового приложения.
    broker_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("broker_accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Биржа (Bybit, Binance)
    exchange: Mapped[str] = mapped_column(String(20), default="Bybit")
    
    # Пара (BTCUSDT)
    symbol: Mapped[str] = mapped_column(String(20))
    
    # Направление (LONG / SHORT)
    side: Mapped[str] = mapped_column(String(10))
    
    # Цены
    entry_price: Mapped[float] = mapped_column(Float)
    exit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Объем позиции (в USDT или монетах)
    amount: Mapped[float] = mapped_column(Float)
    
    # PnL (Прибыль/Убыток)
    pnl: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Статус (OPEN, CLOSED)
    status: Mapped[str] = mapped_column(String(20), default="OPEN")

    # created_at и updated_at наследуются от Base