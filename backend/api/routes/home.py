from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.api.schemas import SuccessResponse
from backend.api.schemas.home import HomeTileCreate, HomeTileUpdate, HomeTileResponse, TileOrderUpdate
from backend.core.deps import get_session, get_admin_user_id
from shared.database.repo.home import HomeRepo

router = APIRouter()

# --- Public API for WebApp ---
@router.get("/layout", response_model=List[HomeTileResponse])
async def get_active_layout(session: AsyncSession = Depends(get_session)):
    repo = HomeRepo(session)
    return await repo.get_all_tiles(active_only=True)

# --- Admin API for Admin WebApp (требует admin auth) ---
@router.get("/admin/layout", response_model=List[HomeTileResponse])
async def get_all_layout(
    session: AsyncSession = Depends(get_session),
    _admin_id: int = Depends(get_admin_user_id),
):
    repo = HomeRepo(session)
    return await repo.get_all_tiles(active_only=False)

@router.post("/admin/layout", response_model=HomeTileResponse)
async def create_tile(
    data: HomeTileCreate,
    session: AsyncSession = Depends(get_session),
    _admin_id: int = Depends(get_admin_user_id),
):
    repo = HomeRepo(session)
    return await repo.create_tile(
        type=data.type,
        size=data.size,
        order=data.order,
        is_active=data.is_active,
        content=data.content
    )

@router.put("/admin/layout/{tile_id}", response_model=HomeTileResponse)
async def update_tile(
    tile_id: int,
    data: HomeTileUpdate,
    session: AsyncSession = Depends(get_session),
    _admin_id: int = Depends(get_admin_user_id),
):
    repo = HomeRepo(session)
    update_data = data.model_dump(exclude_unset=True)
    updated = await repo.update_tile(tile_id, **update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Tile not found")
    return updated

@router.delete("/admin/layout/{tile_id}", response_model=SuccessResponse)
async def delete_tile(
    tile_id: int,
    session: AsyncSession = Depends(get_session),
    _admin_id: int = Depends(get_admin_user_id),
):
    repo = HomeRepo(session)
    deleted = await repo.delete_tile(tile_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tile not found")
    return SuccessResponse()

@router.post("/admin/layout/reorder", response_model=SuccessResponse)
async def reorder_tiles(
    orders: List[TileOrderUpdate],
    session: AsyncSession = Depends(get_session),
    _admin_id: int = Depends(get_admin_user_id),
):
    repo = HomeRepo(session)
    # convert to dict
    orders_dict = [{"id": item.id, "order": item.order} for item in orders]
    await repo.update_orders(orders_dict)
    return SuccessResponse()