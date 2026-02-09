import asyncio
import logging
from sqlalchemy.future import select
from aiogram import Bot
from src.infrastructure.database.main import async_session
from src.infrastructure.database.models import BroadcastQueue, BroadcastSettings, ManagedGroup

logger = logging.getLogger(__name__)

class BroadcastService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self._running = False
        self._task = None

    async def start(self):
        """Start the broadcast service loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("BroadcastService started")

    async def stop(self):
        """Stop the broadcast service loop."""
        if not self._running:
            return
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("BroadcastService stopped")

    async def _loop(self):
        """Main loop for checking and broadcasting links."""
        logger.info("BroadcastService loop started")
        while self._running:
            try:
                async with async_session() as session:
                    res_groups = await session.execute(select(ManagedGroup))
                    groups = res_groups.scalars().all()
                
                # We process each group's check in parallel or sequence. 
                # To keep it simple and respect intervals, let's just run the check once and sleep a standard short duration.
                # Actually, a better way is to check all groups that are "due".
                # But to keep logic simple for now: iterate and process.
                for group in groups:
                    await self._process_group_queue(group.chat_id)
                
            except Exception as e:
                logger.error(f"Error in broadcast loop: {e}", exc_info=True)
            
            # Short sleep to avoid heavy CPU usage, intervals are handled per-send logic eventually or just here?
            # Re-reading: The user wants "frequency" per group.
            # Let's simplify: every 10-30 seconds we check if any group needs a send.
            await asyncio.sleep(10)

    async def _process_group_queue(self, chat_id: int):
        from src.core.services.settings import SettingsService
        
        # 1. Check if active for this chat
        is_active = await SettingsService.get_setting(chat_id, "broadcast_active")
        if not is_active:
            return

        # 2. Check timing (last sent)
        # We can use ChatState or a local cache to track last send time.
        # Let's use ChatState for persistence.
        async with async_session() as session:
            from src.infrastructure.database.models import ChatState
            res = await session.execute(
                select(ChatState).where(ChatState.chat_id == chat_id, ChatState.key == "bc_last_send")
            )
            state = res.scalars().first()
            last_send_str = state.value if state else "0"
            last_send = float(last_send_str)
            
            interval = int(await SettingsService.get_setting_str(chat_id, "broadcast_interval", "60"))
            
            # To make it work with real time across restarts, let's use timestamp instead of loop time
            import time
            current_time = time.time()
            if (current_time - last_send) < interval:
                return

            # 3. Get next pending link for THIS chat
            res_link = await session.execute(
                select(BroadcastQueue)
                .where(BroadcastQueue.sent == 0, BroadcastQueue.chat_id == chat_id)
                .order_by(BroadcastQueue.added_at.asc())
                .limit(1)
            )
            item = res_link.scalars().first()
            
            if not item:
                return

            # 4. Send
            try:
                await self.bot.send_message(
                    chat_id, 
                    item.link,
                    disable_web_page_preview=True
                )
                logger.info(f"Broadcasted to {chat_id}: {item.link}")
                
                # 5. Mark as sent and update last_send
                item.sent = 1
                if not state:
                    state = ChatState(chat_id=chat_id, key="bc_last_send")
                    session.add(state)
                state.value = str(time.time())
                await session.commit()
                
            except Exception as e:
                logger.error(f"Failed to send broadcast to {chat_id}: {e}")
