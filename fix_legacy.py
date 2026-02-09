import asyncio
from sqlalchemy.future import select
from src.infrastructure.database.main import async_session
from src.infrastructure.database.models import BroadcastQueue, ManagedGroup
from src.core.services.settings import SettingsService

async def fix():
    async with async_session() as session:
        # 1. Identity primary group (the one with -100 prefix and most likely the correct one)
        res_groups = await session.execute(select(ManagedGroup))
        groups = res_groups.scalars().all()
        
        target_id = -1003731773907 # Based on logs, this is the active group
        
        print(f"Fixing legacy links for group: {target_id}")
        
        # 2. Update NULL chat_ids
        res_q = await session.execute(select(BroadcastQueue).where(BroadcastQueue.chat_id == None))
        legacy_links = res_q.scalars().all()
        print(f"Found {len(legacy_links)} legacy links. Updating...")
        for link in legacy_links:
            link.chat_id = target_id
        
        # 3. Enable broadcasting for this group if it was disabled during refactor
        await SettingsService.set_setting(target_id, "broadcast_active", "true")
        print("Broadcasting re-enabled for target group.")
        
        await session.commit()
        print("Cleanup complete.")

if __name__ == "__main__":
    asyncio.run(fix())
