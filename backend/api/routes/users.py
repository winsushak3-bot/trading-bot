from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from backend.core.deps import get_session, get_admin_user_id
from shared.database.repo.users import UserRepo
from shared.database.models.accounts import BrokerAccount
from shared.database.models.support import Ticket

router = APIRouter()


class AdminUserResponse(BaseModel):
    id: int
    tg_id: int
    username: Optional[str]
    nickname: Optional[str]
    language: str
    referrals_count: int
    notifications_enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminUsersListResponse(BaseModel):
    users: list[AdminUserResponse]
    total: int


class AdminStatsResponse(BaseModel):
    total_users: int
    new_today: int
    new_week: int
    with_notifications: int
    with_nickname: int
    broker_accounts: int
    tickets_new: int


@router.get("/admin/stats", response_model=AdminStatsResponse)
async def get_stats(
    session: AsyncSession = Depends(get_session),
    _admin_id: int = Depends(get_admin_user_id),
):
    repo = UserRepo(session)
    user_stats = await repo.get_user_stats()

    broker_count = (await session.execute(
        select(func.count()).select_from(BrokerAccount).where(BrokerAccount.is_active == True)
    )).scalar_one()

    tickets_new = (await session.execute(
        select(func.count()).select_from(Ticket).where(Ticket.status == "new")
    )).scalar_one()

    return AdminStatsResponse(
        total_users=user_stats["total"],
        new_today=user_stats["new_today"],
        new_week=user_stats["new_week"],
        with_notifications=user_stats["with_notifications"],
        with_nickname=user_stats["with_nickname"],
        broker_accounts=broker_count,
        tickets_new=tickets_new,
    )


@router.get("/admin/users", response_model=AdminUsersListResponse)
async def list_users(
    limit: int = 20,
    offset: int = 0,
    search: str = "",
    session: AsyncSession = Depends(get_session),
    _admin_id: int = Depends(get_admin_user_id),
):
    repo = UserRepo(session)
    users = await repo.get_all_users(limit=limit, offset=offset, search=search)
    total = await repo.count_users(search=search)
    return AdminUsersListResponse(
        users=[AdminUserResponse.model_validate(u) for u in users],
        total=total,
    )
