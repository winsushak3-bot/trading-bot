# database/repo/support.py
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database.models import Ticket, TicketMessage
from shared.database.repo.base import BaseRepo

class SupportRepo(BaseRepo):
    # === ЮЗЕРСКАЯ ЧАСТЬ ===
    
    async def get_active_ticket(self, user_id: int) -> Ticket | None:
        """Ищет незакрытый тикет юзера"""
        stmt = select(Ticket).where(
            (Ticket.user_id == user_id) & (Ticket.status != 'closed')
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_ticket(self, user_id: int, user_nick: str) -> Ticket:
        """Создает новый тикет"""
        ticket = Ticket(user_id=user_id, user_nick=user_nick, status='new')
        self.session.add(ticket)
        await self.session.flush()
        return ticket

    async def add_message(self, ticket_id: int, sender: str, text: str):
        """Добавляет сообщение в базу"""
        msg = TicketMessage(ticket_id=ticket_id, sender=sender, text=text)
        self.session.add(msg)
        
        # Обновляем время тикета и статус (если ответил админ -> active)
        status_update = {}
        if sender == 'admin':
            status_update['status'] = 'active'
            
        # Всегда обновляем updated_at (автоматически через onupdate в модели, но можно и явно)
        if status_update:
            await self.session.execute(
                update(Ticket).where(Ticket.id == ticket_id).values(**status_update)
            )
            
        await self.session.flush()

    # === АДМИНСКАЯ ЧАСТЬ ===

    async def get_tickets_by_status(self, status: str):
        """Получить список тикетов по статусу"""
        stmt = select(Ticket).where(Ticket.status == status).order_by(Ticket.updated_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_ticket_by_id(self, ticket_id: int) -> Ticket | None:
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_ticket_history(self, ticket_id: int):
        """Получить переписку"""
        stmt = select(TicketMessage).where(TicketMessage.ticket_id == ticket_id).order_by(TicketMessage.created_at.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def close_ticket(self, ticket_id: int):
        stmt = update(Ticket).where(Ticket.id == ticket_id).values(status='closed')
        await self.session.execute(stmt)
        await self.session.flush()
        
    async def get_counts(self):
        """Счетчики для меню (Новые: 5, В работе: 2) — один запрос через GROUP BY."""
        stmt = (
            select(Ticket.status, func.count())
            .group_by(Ticket.status)
        )
        result = await self.session.execute(stmt)
        counts = {row[0]: row[1] for row in result.all()}
        return {
            "new": counts.get("new", 0),
            "active": counts.get("active", 0),
            "closed": counts.get("closed", 0),
        }