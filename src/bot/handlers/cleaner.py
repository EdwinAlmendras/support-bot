import logging
import hashlib
import re
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.future import select
from src.infrastructure.database.main import async_session
from src.infrastructure.database.models import SeenLink
from src.bot.filters.admin import AdminFilter
from src.core.services.settings import SettingsService

router = Router()
logger = logging.getLogger(__name__)

URL_PATTERN = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')



@router.message(F.left_chat_member)
async def on_user_left(message: Message):
    """Auto-delete 'user left' service messages."""
    if not await SettingsService.get_setting(message.chat.id, "delete_joins"):
        return

    try:
        await message.delete()
        logger.info(f"Deleted left message in chat {message.chat.id}")
    except Exception as e:
        logger.error(f"Failed to delete left message: {e}")

@router.message(F.text | F.caption)
async def check_duplicates(message: Message):
    """Check for duplicate links and delete them."""
    logger.info(f"Received message in chat {message.chat.id}: {message.text or message.caption}")
    
    is_enabled = await SettingsService.get_setting(message.chat.id, "delete_links")
    logger.info(f"Delete links enabled: {is_enabled}")
    
    if not is_enabled:
        return

    # Allow admins to bypass
    admin_filter = AdminFilter()
    if await admin_filter(message):
        logger.info("User is admin, bypassing check")
        return

    text = message.text or message.caption or ""
    links = URL_PATTERN.findall(text)
    logger.info(f"Found links: {links}")
    
    if not links:
        return

    async with async_session() as session:
        # Check all links
        # We need to know which ones exist
        hashes = [hashlib.md5(l.encode()).hexdigest() for l in links]
        
        result = await session.execute(
            select(SeenLink).where(
                SeenLink.chat_id == message.chat.id,
                SeenLink.hash.in_(hashes)
            )
        )
        existing_hashes = {row.hash for row in result.scalars().all()}
        
        # Logic: Delete ONLY if ALL links are present
        if len(existing_hashes) == len(hashes):
            logger.info("All links are duplicates. Deleting message.")
            try:
                await message.delete()
            except Exception:
                pass
            return

        # Else, save the new ones
        for link, h in zip(links, hashes):
            if h not in existing_hashes:
                logger.info(f"Saving new link: {link}")
                new_link = SeenLink(chat_id=message.chat.id, hash=h, url=link)
                session.add(new_link)
        
        await session.commit()
