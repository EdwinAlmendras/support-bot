from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from src.bot.filters.admin import AdminFilter
from src.core.services.settings import SettingsService
from src.bot.keyboards.admin import get_settings_keyboard

router = Router()
router.message.filter(AdminFilter())

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    settings = await SettingsService.get_all_settings()
    kb = get_settings_keyboard(settings)
    await message.answer("🔧 **Admin Dashboard**\n\nToggle features below:", reply_markup=kb)

@router.callback_query(F.data.startswith("toggle_"))
async def on_toggle(callback: CallbackQuery):
    key = callback.data.split("_", 1)[1]
    new_state = await SettingsService.toggle_setting(key)
    
    # Update UI
    settings = await SettingsService.get_all_settings()
    kb = get_settings_keyboard(settings)
    
    try:
        await callback.message.edit_reply_markup(reply_markup=kb)
    except Exception:
        pass # Not modified
        
    await callback.answer(f"{key} set to {new_state}")
