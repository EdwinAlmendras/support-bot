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

@router.message(F.new_chat_members)
async def on_user_join(message: Message):
    """Auto-delete 'user joined' service messages."""
    if not await SettingsService.get_setting("delete_joins"):
        return
        
    try:
        await message.delete()
        logger.info(f"Deleted join message in chat {message.chat.id}")
    except Exception as e:
        logger.error(f"Failed to delete join message: {e}")

@router.message(F.left_chat_member)
async def on_user_left(message: Message):
    """Auto-delete 'user left' service messages."""
    if not await SettingsService.get_setting("delete_joins"):
        return

    try:
        await message.delete()
        logger.info(f"Deleted left message in chat {message.chat.id}")
    except Exception as e:
        logger.error(f"Failed to delete left message: {e}")

@router.message(F.text)
async def check_duplicates(message: Message):
    """Check for duplicate links and delete them."""
    if not await SettingsService.get_setting("delete_links"):
        return

    # Allow admins to bypass
    admin_filter = AdminFilter()
    if await admin_filter(message):
        return

    text = message.text or ""
    links = URL_PATTERN.findall(text)
    
    if not links:
        return

    async with async_session() as session:
        for link in links:
            link_hash = hashlib.md5(link.encode()).hexdigest()
            
            # Check if link exists in this chat
            result = await session.execute(
                select(SeenLink).where(
                    SeenLink.chat_id == message.chat.id,
                    SeenLink.link_hash == link_hash
                )
            )
            existing = result.scalars().first()
            
            if existing:
                await message.delete()
                return # Delete once and exit
            
            # Add new link
            new_link = SeenLink(chat_id=message.chat.id, link_hash=link_hash)
            session.add(new_link)
        
        await session.commit()
