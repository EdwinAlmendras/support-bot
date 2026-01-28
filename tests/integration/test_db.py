import pytest
from sqlalchemy import select
from src.infrastructure.database.models import SeenLink

@pytest.mark.asyncio
async def test_create_and_retrieve_link(db_session):
    # Arrange
    chat_id = 100
    link_hash = "abc123hash"
    
    # Act
    new_link = SeenLink(chat_id=chat_id, link_hash=link_hash)
    db_session.add(new_link)
    await db_session.commit()
    
    # Assert
    result = await db_session.execute(
        select(SeenLink).where(SeenLink.chat_id == chat_id)
    )
    link = result.scalars().first()
    
    assert link is not None
    assert link.link_hash == link_hash
    assert link.id is not None
