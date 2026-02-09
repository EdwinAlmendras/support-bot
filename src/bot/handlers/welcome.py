from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery 
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.bot.filters.admin import AdminFilter
from src.core.services.welcome import WelcomeService
from src.core.services.settings import SettingsService
import os

router = Router()

class WelcomeEdit(StatesGroup):
    waiting_for_input = State()
    editing_key = State()

@router.message(F.new_chat_members)
async def on_user_join(message: Message, bot: Bot):
    # 1. Delete Service Message if enabled
    if await SettingsService.get_setting(message.chat.id, "delete_joins"):
        try:
            await message.delete()
        except Exception:
            pass

    # 2. Check if welcome is enabled
    if not await SettingsService.get_setting(message.chat.id, "welcome_enabled"):
        return
    
    for member in message.new_chat_members:
        if member.is_bot:
            continue
        await WelcomeService.add_to_queue(bot, message.chat.id, member.first_name, member.id)

# Admin Edit Handlers

@router.callback_query(F.data.startswith("edit_welcome_"))
async def start_edit_welcome(callback: CallbackQuery, state: FSMContext):
    if str(callback.from_user.id) not in os.getenv("ADMIN_IDS", "").split(","):
        await callback.answer("⛔ Unauthorized", show_alert=True)
        return

    # Data: edit_welcome_{target_id}_{key}
    parts = callback.data.split("_")
    # parts[0]=edit, parts[1]=welcome, parts[2]=target_id, parts[3:]=key
    
    target_id = int(parts[2])
    key = "_".join(parts[3:])
    
    await state.update_data(key=key, target_id=target_id)
    await state.set_state(WelcomeEdit.waiting_for_input)
    
    # Check if we should delete menu? 
    # Logic: if in DM, we probably shouldn't delete the "Select Group" history if user wants to go back?
    # But user asked "el mensaje una vez psuldao el boton se debe elimainr".
    # Let's delete for cleanliness.
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    readable = key.replace("welcome_", "").replace("_", " ").capitalize()
    default_val = WelcomeService.WELCOME_DEFAULTS.get(key, "Not set")
    current_value = await SettingsService.get_setting_str(target_id, key, default_val)
    
    text = (
        f"Send me the new **{readable}** for Group {target_id}:\n\n"
        f"**Current value:**\n`{current_value}`"
    )
    
    await callback.message.answer(text)
    await callback.answer()

@router.message(StateFilter(WelcomeEdit.waiting_for_input))
async def save_welcome_setting(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    key = data.get("key")
    target_id = data.get("target_id")
    
    if not target_id:
        await message.answer("⚠️ Error: Target group lost. Please start over.")
        await state.clear()
        return

    value = None
    
    # Handle Photo Upload for Image
    if key == "welcome_image" and message.photo:
        value = message.photo[-1].file_id
    elif message.text:
        value = message.text
    
    if not value:
        await message.answer("⚠️ Please send text or a valid photo.")
        return

    await SettingsService.set_setting(target_id, key, value)
    
    # Cleanup input
    try:
        await message.delete()
    except Exception:
        pass

    # Single confirmation (SILENT)
    
    # Use fake name for preview to the ADMIN (in DM)
    # We send the preview to the ADMIN (message.chat.id), but identifying as the group?
    # No, we just show what it looks like.
    # We need to simulate the group welcome.
    
    # But wait, send_welcome_message sends to `chat_id`. 
    # If we pass `target_id`, it sends to the GROUP.
    # We want to show preview to the ADMIN in DM.
    
    # So we need a way to generate the preview but send to a specific chat (admin DM).
    # send_welcome_message uses `target_id` to FETCH settings.
    # And sends to `chat_id`.
    # Current signature: `send_welcome_message(bot, chat_id, user_first_name)`
    # It fetches settings from `chat_id` and sends to `chat_id`.
    
    # Single confirmation (SILENT)
    # Use fake name for preview to the ADMIN (in DM)
    try:
        sent = await WelcomeService.send_welcome_message(
            bot=bot, 
            chat_id=message.chat.id, 
            user_first_name="PreviewUser", 
            user_id=message.from_user.id,
            settings_chat_id=target_id
        )
        if sent:
            # Auto-delete preview after 10s
            await asyncio.sleep(10)
            await sent.delete()
    except Exception:
        pass
    
    await state.clear()

@router.callback_query(F.data.startswith("preview_welcome_"))
async def preview_welcome_callback(callback: CallbackQuery, bot: Bot):
    if str(callback.from_user.id) not in os.getenv("ADMIN_IDS", "").split(","):
        await callback.answer("⛔ Unauthorized", show_alert=True)
        return

    target_id = int(callback.data.split("_")[2])
    
    try:
        sent = await WelcomeService.send_welcome_message(
            bot=bot,
            chat_id=callback.message.chat.id,
            user_first_name="PreviewUser",
            user_id=callback.from_user.id,
            settings_chat_id=target_id
        )
        if sent:
            await callback.answer("Preview sent!")
            # Auto-delete preview after 10s
            await asyncio.sleep(10)
            await sent.delete()
        else:
            await callback.answer("⚠️ Error generating preview.", show_alert=True)
    except Exception as e:
        await callback.answer(f"❌ Error: {e}", show_alert=True)
