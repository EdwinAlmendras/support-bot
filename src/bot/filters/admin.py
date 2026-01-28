from aiogram.filters import BaseFilter
from aiogram.types import Message
import os

class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        admin_ids = os.getenv("ADMIN_IDS", "").split(",")
        return str(message.from_user.id) in admin_ids
