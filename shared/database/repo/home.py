from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from shared.database.models.home import HomeTile
from shared.database.repo.base import BaseRepo

class HomeRepo(BaseRepo):
    async def get_all_tiles(self, active_only: bool = False) -> List[HomeTile]:
        stmt = select(HomeTile).order_by(HomeTile.order)
        if active_only:
            stmt = stmt.where(HomeTile.is_active.is_(True))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_tile(self, type: str, size: str, order: int, is_active: bool, content: Dict[str, Any]) -> HomeTile:
        tile = HomeTile(
            type=type,
            size=size,
            order=order,
            is_active=is_active,
            content=content
        )
        self.session.add(tile)
        await self.session.flush()
        await self.session.refresh(tile)
        return tile

    async def update_tile(self, tile_id: int, **kwargs) -> Optional[HomeTile]:
        if not kwargs:
            return await self.session.get(HomeTile, tile_id)
            
        stmt = update(HomeTile).where(HomeTile.id == tile_id).values(**kwargs).returning(HomeTile)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_tile(self, tile_id: int) -> bool:
        stmt = delete(HomeTile).where(HomeTile.id == tile_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def update_orders(self, orders: List[Dict[str, int]]):
        for item in orders:
            stmt = update(HomeTile).where(HomeTile.id == item["id"]).values(order=item["order"])
            await self.session.execute(stmt)