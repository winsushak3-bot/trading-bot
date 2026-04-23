"""Quick diagnostic: read tiles directly from DB via HomeRepo."""
import asyncio
import sys
import os

# allow running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.utils.asyncio_policy import apply_windows_event_loop_policy
apply_windows_event_loop_policy()

from shared.database.core import session_maker
from shared.database.repo.home import HomeRepo


async def main():
    async with session_maker() as s:
        repo = HomeRepo(s)
        active = await repo.get_all_tiles(active_only=True)
        all_t = await repo.get_all_tiles(active_only=False)
        print(f"Active tiles (public /home/layout): {len(active)}")
        print(f"All tiles (admin /home/admin/layout): {len(all_t)}")
        for t in all_t:
            content = t.content or {}
            title = content.get("title", "<no title>")
            print(f"  id={t.id}  type={t.type}  active={t.is_active}  order={t.order}  title={title!r}")


asyncio.run(main())
