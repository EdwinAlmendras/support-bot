from sqlalchemy import select, update
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from src.infrastructure.database.main import async_session
from src.infrastructure.database.models import BotSetting

# Defaults
DEFAULT_SETTINGS = {
    "delete_links": "true",
    "delete_joins": "true",
    "welcome_enabled": "true",
}

class SettingsService:
    @staticmethod
    async def get_setting(chat_id: int, key: str) -> bool:
        async with async_session() as session:
            result = await session.execute(
                select(BotSetting).where(BotSetting.chat_id == chat_id, BotSetting.key == key)
            )
            setting = result.scalars().first()
            
            val = setting.value if setting else DEFAULT_SETTINGS.get(key, "false")
            return val.lower() == "true"

    @staticmethod
    async def toggle_setting(chat_id: int, key: str) -> bool:
        async with async_session() as session:
            # Check current
            result = await session.execute(
                select(BotSetting).where(BotSetting.chat_id == chat_id, BotSetting.key == key)
            )
            setting = result.scalars().first()
            
            new_val = "true"
            if setting:
                new_val = "false" if setting.value.lower() == "true" else "true"
                setting.value = new_val
                await session.merge(setting)
            else:
                current = DEFAULT_SETTINGS.get(key, "false")
                new_val = "false" if current == "true" else "true"
                session.add(BotSetting(chat_id=chat_id, key=key, value=new_val))
            
            await session.commit()
            return new_val == "true"

    @staticmethod
    async def get_all_settings(chat_id: int):
        settings = DEFAULT_SETTINGS.copy()
        async with async_session() as session:
            result = await session.execute(
                select(BotSetting).where(BotSetting.chat_id == chat_id)
            )
            db_settings = result.scalars().all()
            for s in db_settings:
                settings[s.key] = s.value
        return settings

    @staticmethod
    async def get_setting_str(chat_id: int, key: str, default: str = "") -> str:
        async with async_session() as session:
            result = await session.execute(
                select(BotSetting).where(BotSetting.chat_id == chat_id, BotSetting.key == key)
            )
            setting = result.scalars().first()
            return setting.value if setting else default
            
    @staticmethod
    async def set_setting(chat_id: int, key: str, value: str):
        async with async_session() as session:
            result = await session.execute(
                select(BotSetting).where(BotSetting.chat_id == chat_id, BotSetting.key == key)
            )
            setting = result.scalars().first()
            if setting:
                setting.value = value
            else:
                session.add(BotSetting(chat_id=chat_id, key=key, value=value))
            await session.commit()
