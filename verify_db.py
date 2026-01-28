import asyncio
import os
from src.infrastructure.database.main import init_db, get_session
from src.infrastructure.database.models import SeenLink
from sqlalchemy import select

async def test_db():
    print("Initializing DB...")
    await init_db()
    
    print("Testing verification...")
    async for session in get_session():
        # Test insert
        link_hash = "test_hash_123"
        chat_id = 12345
        
        new_link = SeenLink(chat_id=chat_id, link_hash=link_hash)
        session.add(new_link)
        await session.commit()
        
        # Test select
        result = await session.execute(
            select(SeenLink).where(
                SeenLink.chat_id == chat_id,
                SeenLink.link_hash == link_hash
            )
        )
        existing = result.scalars().first()
        
        if existing:
            print("SUCCESS: Link found in DB")
        else:
            print("FAILURE: Link not found")
            
        # Clean up
        await session.delete(existing)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(test_db())
