from sqlalchemy import select, update
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from src.infrastructure.database.main import async_session
from src.infrastructure.database.models import BotSetting

# Defaults
DEFAULT_SETTINGS = {
    "delete_links": "true",
    "delete_joins": "true",
}

class SettingsService:
    @staticmethod
    async def get_setting(key: str) -> bool:
        async with async_session() as session:
            result = await session.execute(
                select(BotSetting).where(BotSetting.key == key)
            )
            setting = result.scalars().first()
            
            val = setting.value if setting else DEFAULT_SETTINGS.get(key, "false")
            return val.lower() == "true"

    @staticmethod
    async def toggle_setting(key: str) -> bool:
        async with async_session() as session:
            # Check current
            result = await session.execute(
                select(BotSetting).where(BotSetting.key == key)
            )
            setting = result.scalars().first()
            
            new_val = "true"
            if setting:
                new_val = "false" if setting.value.lower() == "true" else "true"
                setting.value = new_val
                await session.merge(setting)
            else:
                new_val = "false" if DEFAULT_SETTINGS.get(key) == "true" else "true"
                # If not exists but default is true, toggling means setting to false
                # This logic is slightly complex, let's simplify:
                # If not in DB, assume default.
                current = DEFAULT_SETTINGS.get(key, "false")
                new_val = "false" if current == "true" else "true"
                session.add(BotSetting(key=key, value=new_val))
            
            await session.commit()
            return new_val == "true"

    @staticmethod
    async def get_all_settings():
        settings = DEFAULT_SETTINGS.copy()
        async with async_session() as session:
            result = await session.execute(select(BotSetting))
            db_settings = result.scalars().all()
            for s in db_settings:
                settings[s.key] = s.value
        return settings

    @staticmethod
    async def get_setting_str(key: str, default: str = "") -> str:
        async with async_session() as session:
            result = await session.execute(
                select(BotSetting).where(BotSetting.key == key)
            )
            setting = result.scalars().first()
            return setting.value if setting else default
            
    @staticmethod
    async def set_setting(key: str, value: str):
        async with async_session() as session:
            result = await session.execute(
                select(BotSetting).where(BotSetting.key == key)
            )
            setting = result.scalars().first()
            if setting:
                setting.value = value
            else:
                session.add(BotSetting(key=key, value=value))
            await session.commit()
