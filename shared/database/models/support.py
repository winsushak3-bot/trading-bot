# database/models/support.py
from sqlalchemy import BigInteger, String, Integer, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class Ticket(Base):
    __tablename__ = "tickets"

    __table_args__ = (
        # Быстрый выбор тикетов по статусу с сортировкой по свежести (get_tickets_by_status)
        Index("ix_tickets_status_updated", "status", "updated_at"),
        # Общая сортировка по дате создания
        Index("ix_tickets_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # ИСПРАВЛЕНИЕ: Делаем явную связь с users.tg_id
    user_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey("users.tg_id", ondelete="CASCADE"), 
        index=True
    ) 
    
    user_nick: Mapped[str | None] = mapped_column(String(32))    
    status: Mapped[str] = mapped_column(String(10), default="new")

    # created_at и updated_at наследуются от Base

class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    __table_args__ = (
        # История переписки тикета читается в порядке created_at
        Index("ix_ticket_messages_ticket_created", "ticket_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    sender: Mapped[str] = mapped_column(String(10)) 
    text: Mapped[str] = mapped_column(Text)

    # created_at и updated_at наследуются от Base