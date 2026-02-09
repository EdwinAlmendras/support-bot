import asyncio
from src.infrastructure.database.models import Base, BotSetting
from src.infrastructure.database.main import engine

async def inspect():
    print("Tables in Base.metadata:")
    for t in Base.metadata.tables:
        print(f" - {t}")
        if t == "bot_settings":
            print(f"   Columns: {[c.name for c in Base.metadata.tables[t].columns]}")
            
    print(f"\nBotSetting columns: {[c.name for c in BotSetting.__table__.columns]}")

if __name__ == "__main__":
    asyncio.run(inspect())
