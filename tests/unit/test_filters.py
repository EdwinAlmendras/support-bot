import pytest
import os
from unittest.mock import Mock
from aiogram.types import Message, User, Chat
from src.bot.filters.admin import AdminFilter

@pytest.mark.asyncio
async def test_admin_filter_matches():
    # Setup
    os.environ["ADMIN_IDS"] = "12345,67890"
    filter_ = AdminFilter()
    
    # Mock Message from Admin
    user = User(id=12345, is_bot=False, first_name="Admin")
    chat = Chat(id=1, type="private")
    message = Mock(spec=Message)
    message.from_user = user
    message.chat = chat
    
    # Assert
    assert await filter_(message) is True

@pytest.mark.asyncio
async def test_admin_filter_rejects_non_admin():
    # Setup
    os.environ["ADMIN_IDS"] = "12345"
    filter_ = AdminFilter()
    
    # Mock Message from User
    user = User(id=99999, is_bot=False, first_name="User")
    message = Mock(spec=Message)
    message.from_user = user
    
    # Assert
    assert await filter_(message) is False
