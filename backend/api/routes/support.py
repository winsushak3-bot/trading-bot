from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.schemas.support import (
    TicketResponse, TicketMessageResponse, 
    TicketMessageCreate, SupportCountsResponse, TicketWithMessages
)
from backend.api.schemas import SuccessResponse
from backend.core.deps import get_session, get_current_user_id, get_admin_user_id
from shared.database.repo.support import SupportRepo
from shared.database.repo.users import UserRepo

router = APIRouter()

# === ЮЗЕРСКИЕ РОУТЫ ===

@router.get("/my-ticket", response_model=TicketWithMessages)
async def get_my_ticket(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """Получает активный тикет юзера и его сообщения"""
    support_repo = SupportRepo(session)
    ticket = await support_repo.get_active_ticket(user_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="No active ticket found")
    
    messages = await support_repo.get_ticket_history(ticket.id)
    
    return TicketWithMessages(
        id=ticket.id,
        user_id=ticket.user_id,
        user_nick=ticket.user_nick,
        status=ticket.status,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        messages=[TicketMessageResponse.model_validate(m) for m in messages]
    )

@router.post("/my-ticket", response_model=TicketResponse)
async def create_my_ticket(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """Создает новый тикет для юзера"""
    support_repo = SupportRepo(session)
    
    # Проверяем нет ли уже активного
    existing = await support_repo.get_active_ticket(user_id)
    if existing:
        return TicketResponse.model_validate(existing)
        
    user_repo = UserRepo(session)
    user = await user_repo.get_user(user_id)
    
    # Если юзера нет в БД, попробуем его создать (чтобы не было ошибки Foreign Key)
    if not user:
        try:
            user = await user_repo.create_user(tg_id=user_id, username="User", language="ru")
        except Exception as e:
            raise HTTPException(status_code=500, detail="Could not create user for ticket")

    user_nick = getattr(user, 'nickname', getattr(user, 'username', 'User')) if user else 'User'
    
    ticket = await support_repo.create_ticket(user_id, user_nick=user_nick)
    await session.flush()
    await session.refresh(ticket)
    return TicketResponse.model_validate(ticket)

@router.post("/ticket/{ticket_id}/message", response_model=TicketMessageResponse)
async def send_message(
    ticket_id: int,
    message: TicketMessageCreate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """Отправляет сообщение в тикет (юзер)"""
    support_repo = SupportRepo(session)
    ticket = await support_repo.get_ticket_by_id(ticket_id)
    if not ticket or ticket.user_id != user_id:
        raise HTTPException(status_code=404, detail="Ticket not found or access denied")
        
    if ticket.status == 'closed':
        raise HTTPException(status_code=400, detail="Ticket is closed")
        
    await support_repo.add_message(ticket_id, sender='user', text=message.text)
    
    # Получаем последнее сообщение для ответа
    messages = await support_repo.get_ticket_history(ticket_id)
    return TicketMessageResponse.model_validate(messages[-1])


# === АДМИНСКИЕ РОУТЫ ===

@router.get("/admin/counts", response_model=SupportCountsResponse)
async def get_support_counts(
    session: AsyncSession = Depends(get_session),
    _admin_id: int = Depends(get_admin_user_id),
):
    """Счетчики тикетов для админки"""
    support_repo = SupportRepo(session)
    counts = await support_repo.get_counts()
    return counts

@router.get("/admin/tickets", response_model=list[TicketResponse])
async def get_tickets(
    status: str = 'new',
    session: AsyncSession = Depends(get_session),
    _admin_id: int = Depends(get_admin_user_id),
):
    """Получает тикеты по статусу для админки"""
    support_repo = SupportRepo(session)
    tickets = await support_repo.get_tickets_by_status(status)
    return [TicketResponse.model_validate(t) for t in tickets]

@router.get("/admin/ticket/{ticket_id}", response_model=TicketWithMessages)
async def get_ticket_details(
    ticket_id: int,
    session: AsyncSession = Depends(get_session),
    _admin_id: int = Depends(get_admin_user_id),
):
    """Детали тикета для админки"""
    support_repo = SupportRepo(session)
    ticket = await support_repo.get_ticket_by_id(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    messages = await support_repo.get_ticket_history(ticket_id)
    return TicketWithMessages(
        id=ticket.id,
        user_id=ticket.user_id,
        user_nick=ticket.user_nick,
        status=ticket.status,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        messages=[TicketMessageResponse.model_validate(m) for m in messages]
    )

@router.post("/admin/ticket/{ticket_id}/message", response_model=TicketMessageResponse)
async def admin_send_message(
    ticket_id: int,
    message: TicketMessageCreate,
    session: AsyncSession = Depends(get_session),
    _admin_id: int = Depends(get_admin_user_id),
):
    """Отвечает на тикет из админки"""
    support_repo = SupportRepo(session)
    ticket = await support_repo.get_ticket_by_id(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    await support_repo.add_message(ticket_id, sender='admin', text=message.text)
    
    messages = await support_repo.get_ticket_history(ticket_id)
    return TicketMessageResponse.model_validate(messages[-1])

@router.post("/admin/ticket/{ticket_id}/close", response_model=SuccessResponse)
async def admin_close_ticket(
    ticket_id: int,
    session: AsyncSession = Depends(get_session),
    _admin_id: int = Depends(get_admin_user_id),
):
    """Закрывает тикет"""
    support_repo = SupportRepo(session)
    await support_repo.close_ticket(ticket_id)
    return SuccessResponse()
