from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery 
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.bot.filters.admin import AdminFilter
from src.core.services.welcome import WelcomeService
from src.core.services.settings import SettingsService

router = Router()

class WelcomeEdit(StatesGroup):
    waiting_for_input = State()
    editing_key = State()

@router.message(F.new_chat_members)
async def on_user_join(message: Message, bot: Bot):
    # Skip if welcome feature disabled (optional check)
    if not await SettingsService.get_setting("welcome_enabled"):
         # Default true if not found?
         pass

    for member in message.new_chat_members:
        if member.is_bot:
            continue
        await WelcomeService.send_welcome(bot, message.chat.id, member.first_name)

# Admin Edit Handlers

@router.callback_query(F.data.startswith("edit_welcome_"))
async def start_edit_welcome(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split("edit_welcome_", 1)[1]
    await state.update_data(key=key)
    await state.set_state(WelcomeEdit.waiting_for_input)
    
    readable = key.replace("welcome_", "").capitalize()
    await callback.message.answer(f"Send me the new **{readable}**:")
    await callback.answer()

@router.message(StateFilter(WelcomeEdit.waiting_for_input))
async def save_welcome_setting(message: Message, state: FSMContext):
    data = await state.get_data()
    key = data.get("key")
    
    value = message.text
    if not value:
        await message.answer("Please send text only.")
        return

    await SettingsService.set_setting(key, value)
    await message.answer(f"✅ Saved! New {key}: `{value}`")
    await state.clear()
