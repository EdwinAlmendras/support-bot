import asyncio
import logging
from typing import Optional
from aiogram import Bot
from sqlalchemy import select, delete
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.infrastructure.database.main import async_session
from src.infrastructure.database.models import ChatState
from src.core.services.settings import SettingsService

logger = logging.getLogger(__name__)

class WelcomeService:
    _queues = {} # {chat_id: asyncio.Queue}
    _workers = {} # {chat_id: Task}

    WELCOME_DEFAULTS = {
        "welcome_image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQM6FIHKRuzAEBC8Fr8AQKNuKwqnzNlwmXDZQ&s",
        "welcome_text": (
            "👋 <b>WELCOME {user}!</b>\n\n"
            "Welcome to <b>{group}</b>. Here you can share your links from "
            "<b>YouTube, TikTok, VK</b> and other social networks with us community! 👾"
        ),
        "welcome_link": "",
        "welcome_button_text": "Share Channel"
    }

    @classmethod
    async def add_to_queue(cls, bot: Bot, chat_id: int, user_first_name: str, user_id: int):
        if chat_id not in cls._queues:
            cls._queues[chat_id] = asyncio.Queue()
        
        await cls._queues[chat_id].put((user_first_name, user_id))
        
        # Start worker if not running
        if chat_id not in cls._workers or cls._workers[chat_id].done():
            cls._workers[chat_id] = asyncio.create_task(cls._worker(bot, chat_id))

    @classmethod
    async def _send_to_logger(cls, text: str):
        # We don't have a logger here but we can use print for now
        print(f"[WelcomeService] {text}")

    @classmethod
    async def send_welcome_message(cls, bot: Bot, chat_id: int, user_first_name: str, user_id: int = None, settings_chat_id: int = None):
        # settings_chat_id: from which chat to pull settings. defaults to chat_id.
        fetch_id = settings_chat_id or chat_id
        
        chat = await bot.get_chat(fetch_id)
        group_name = chat.title or "this group"
        
        # Fetch settings
        img_url = await SettingsService.get_setting_str(fetch_id, "welcome_image", cls.WELCOME_DEFAULTS["welcome_image"])
        text_template = await SettingsService.get_setting_str(fetch_id, "welcome_text", cls.WELCOME_DEFAULTS["welcome_text"])
        group_link = await SettingsService.get_setting_str(fetch_id, "welcome_link", cls.WELCOME_DEFAULTS["welcome_link"])
        btn_text = await SettingsService.get_setting_str(fetch_id, "welcome_button_text", cls.WELCOME_DEFAULTS["welcome_button_text"])
        
        group_link = group_link.strip() if group_link else ""
        
        logger.info(f"Welcome preview for chat {chat_id} (Settings from {fetch_id}): link='{group_link}', btn='{btn_text}'")

        # Mentions for {user}
        user_mention = user_first_name
        if user_id:
            user_mention = f'<a href="tg://user?id={user_id}">{user_first_name}</a>'
        
        formatted_text = text_template.replace("{user}", user_mention).replace("{name}", user_first_name).replace("{group}", group_name)

        # Keyboard
        reply_markup = None
        if group_link and (group_link.startswith("http://") or group_link.startswith("https://") or group_link.startswith("t.me/")):
            # If t.me/ we should probably prepend https:// if missing, but InlineKeyboardButton requires absolute URL
            final_url = group_link
            if not final_url.startswith("http"):
                final_url = "https://" + final_url
                
            reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=btn_text, url=final_url)]
            ])
            logger.info("Button created successfully")
        else:
            logger.warning(f"No button created. Link is: '{group_link}'")

        # Send
        try:
            sent_msg = await bot.send_photo(
                chat_id=chat_id,
                photo=img_url,
                caption=formatted_text,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
            return sent_msg
        except Exception as e:
            logger.error(f"Failed to send welcome: {e}")
            return None

    @classmethod
    async def _worker(cls, bot: Bot, chat_id: int):
        queue = cls._queues[chat_id]
        while not queue.empty():
            # In the queue we now store (user_name, user_id)
            user_data = await queue.get()
            if isinstance(user_data, tuple):
                user_name, user_id = user_data
            else:
                user_name, user_id = user_data, None
            
            msg = await cls.send_welcome_message(bot, chat_id, user_name, user_id)
            
            if msg:
                # Wait 10 seconds
                await asyncio.sleep(10)
                # Delete
                try:
                    await msg.delete()
                except Exception:
                    pass
            
            # Small buffer?
            await asyncio.sleep(0.5)
