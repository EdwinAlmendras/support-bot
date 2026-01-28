import asyncio
from typing import Optional
from aiogram import Bot
from sqlalchemy import select, delete
from src.infrastructure.database.main import async_session
from src.infrastructure.database.models import ChatState
from src.core.services.settings import SettingsService

class WelcomeService:
    _locks = {} # In-memory locks per chat to prevent race conditions

    @staticmethod
    def get_lock(chat_id: int):
        if chat_id not in WelcomeService._locks:
            WelcomeService._locks[chat_id] = asyncio.Lock()
        return WelcomeService._locks[chat_id]

    @staticmethod
    async def send_welcome(bot: Bot, chat_id: int, user_first_name: str):
        # 1. Get Settings (Cached or DB)
        # Using Settings for Content. We'll store content in the same settings table for simplicity
        # keys: "welcome_text", "welcome_image", "welcome_caption"
        
        # Defaults
        default_img = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQM6FIHKRuzAEBC8Fr8AQKNuKwqnzNlwmXDZQ&s"
        default_text = "Welcome {name}! Join our group here: {link}"
        default_link = "https://t.me/share/url?url=https://t.me/yourgroup"
        
        # Fetch configurations (We can optimize this with a single get_all query later)
        # For now, simplistic fetches
        img_url = await SettingsService.get_setting_str("welcome_image", default_img)
        text_template = await SettingsService.get_setting_str("welcome_text", default_text)
        group_link = await SettingsService.get_setting_str("welcome_link", default_link)
        
        formatted_text = text_template.replace("{name}", user_first_name).replace("{link}", group_link)

        # 2. Critical Section: Delete Old -> Send New
        async with WelcomeService.get_lock(chat_id):
            async with async_session() as session:
                # Get last message ID
                result = await session.execute(
                     select(ChatState).where(
                         ChatState.chat_id == chat_id,
                         ChatState.key == "last_welcome_id"
                     )
                )
                state = result.scalars().first()
                
                # Delete old
                if state:
                    try:
                        await bot.delete_message(chat_id, int(state.value))
                    except Exception:
                        pass # Message already deleted or too old
                
                # Send new
                try:
                    sent_msg = await bot.send_photo(
                        chat_id=chat_id,
                        photo=img_url,
                        caption=formatted_text
                    )
                    
                    # Update State
                    if state:
                        state.value = str(sent_msg.message_id)
                    else:
                        state = ChatState(chat_id=chat_id, key="last_welcome_id", value=str(sent_msg.message_id))
                        session.add(state)
                    
                    await session.commit()
                except Exception as e:
                    print(f"Failed to send welcome: {e}")
