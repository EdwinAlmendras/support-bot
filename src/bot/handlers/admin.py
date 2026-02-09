import os
from aiogram import Router, F, Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.future import select
from sqlalchemy import func
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.bot.filters.admin import AdminFilter
from src.core.services.settings import SettingsService
from src.bot.keyboards.admin import get_settings_keyboard, get_group_selection_keyboard
from src.bot.keyboards.broadcast import get_broadcast_keyboard

router = Router()
router.message.filter(AdminFilter())

from aiogram.filters import CommandObject
from sqlalchemy import delete
from src.infrastructure.database.main import async_session
from src.infrastructure.database.models import ManagedGroup, BroadcastQueue, BroadcastSettings

class BroadcastStates(StatesGroup):
    waiting_for_group = State()
    waiting_for_link = State()
    waiting_for_interval = State()
    target_id = State() # To store the selected chat_id

class ExpiringMessageStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_duration = State()

@router.message(Command("addgroup"))
async def cmd_addgroup(message: Message, command: CommandObject, bot: Bot):
    if str(message.from_user.id) not in os.getenv("ADMIN_IDS", "").split(","):
        return

    if not command.args:
        await message.answer("Usage: `/addgroup -100xxxx`")
        return

    try:
        chat_id = int(command.args.strip())
    except ValueError:
        await message.answer("Invalid ID.")
        return

    # Try to fetch group name from Telegram
    group_name = "Group"
    try:
        chat = await bot.get_chat(chat_id)
        group_name = chat.title or "Group"
    except Exception:
        # Auto-retry with -100 if the ID doesn't have it
        if not str(chat_id).startswith("-100") and str(chat_id).startswith("-"):
            try:
                alt_id = int("-100" + str(chat_id)[1:])
                chat = await bot.get_chat(alt_id)
                chat_id = alt_id
                group_name = chat.title or "Group"
            except Exception as e:
                await message.answer(f"⚠️ Warning: Could not fetch group title. Ensure the bot is in the group and the ID is correct.\nError: {e}")
        else:
            await message.answer("⚠️ Warning: Could not fetch group title. Chat not found.")

    async with async_session() as session:
        # Check if exists
        res = await session.execute(select(ManagedGroup).where(ManagedGroup.chat_id == chat_id))
        existing = res.scalars().first()
        if existing:
            existing.name = group_name # Update name if already exists
            await message.answer(f"🔄 Group already managed. Updated name to: **{group_name}**")
        else:
            new_group = ManagedGroup(chat_id=chat_id, name=group_name)
            session.add(new_group)
            await message.answer(f"✅ Added group: **{group_name}** (`{chat_id}`)")
        
        await session.commit()

@router.message(Command("delgroup"))
async def cmd_delgroup(message: Message, command: CommandObject):
    if str(message.from_user.id) not in os.getenv("ADMIN_IDS", "").split(","):
        return

    if not command.args:
        await message.answer("Usage: `/delgroup -100xxxx`")
        return

    try:
        chat_id = int(command.args.strip())
    except ValueError:
        await message.answer("Invalid ID.")
        return

    async with async_session() as session:
        await session.execute(delete(ManagedGroup).where(ManagedGroup.chat_id == chat_id))
        await session.commit()
    
    await message.answer(f"🗑️ Removed group `{chat_id}`")

@router.message(Command("mygroups"))
async def cmd_mygroups(message: Message):
    if str(message.from_user.id) not in os.getenv("ADMIN_IDS", "").split(","):
        return

    async with async_session() as session:
        result = await session.execute(select(ManagedGroup))
        groups = result.scalars().all()
    
    if not groups:
        await message.answer("No managed groups found.")
        return
        
    text = "**Managed Groups:**\n" + "\n".join([f"• `{g.chat_id}`" for g in groups])
    await message.answer(text)

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.chat.type != "private":
        pass

    async with async_session() as session:
        result = await session.execute(select(ManagedGroup))
        groups = result.scalars().all()
    
    if not groups:
        await message.answer("⚠️ No groups managed. Use `/addgroup <id>` to add one.")
        return

    if len(groups) == 1:
        target_id = groups[0].chat_id
        target_name = groups[0].name or str(target_id)
        settings = await SettingsService.get_all_settings(target_id)
        kb = get_settings_keyboard(settings, target_id)
        await message.answer(f"🔧 **Admin Dashboard**\nGroup: **{target_name}**\n\nToggle features below:", reply_markup=kb)
    else:
        kb = get_group_selection_keyboard(groups)
        await message.answer("Please select a group to manage:", reply_markup=kb)

@router.callback_query(F.data.startswith("select_group_"))
async def on_select_group(callback: CallbackQuery, bot: Bot):
    # This is for the /admin dashboard selection
    target_id = int(callback.data.split("_")[2])
    
    # Fetch name
    group_name = "Group"
    async with async_session() as session:
        res = await session.execute(select(ManagedGroup).where(ManagedGroup.chat_id == target_id))
        g = res.scalars().first()
        if g:
            group_name = g.name or str(target_id)
            
    settings = await SettingsService.get_all_settings(target_id)
    kb = get_settings_keyboard(settings, target_id)
    
    await callback.message.edit_text(f"🔧 **Admin Dashboard**\nGroup: **{group_name}**\n\nToggle features below:", reply_markup=kb)

@router.callback_query(F.data.startswith("bc_select_group_"))
async def on_bc_select_group(callback: CallbackQuery, bot: Bot):
    # This is for the /broadcast dashboard selection
    target_id = int(callback.data.split("_")[3])
    
    async with async_session() as session:
        res = await session.execute(select(ManagedGroup).where(ManagedGroup.chat_id == target_id))
        g = res.scalars().first()
        group_name = g.name if g else str(target_id)

        # Get broadcast status for this group via SettingsService
        # No, Broadcaster still uses its own settings table for now or we migrate?
        # Let's use SettingsService for "broadcast_active" and "broadcast_interval" to be consistent.
        is_active = await SettingsService.get_setting(target_id, "broadcast_active")
    
    kb = get_broadcast_keyboard(is_active, target_id)
    await callback.message.edit_text(
        f"📡 **Broadcaster Dashboard**\nGroup: **{group_name}**\nManage automated links here:", 
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data.startswith("toggle_"))
async def on_toggle(callback: CallbackQuery):
    if str(callback.from_user.id) not in os.getenv("ADMIN_IDS", "").split(","):
        await callback.answer("⛔ Unauthorized", show_alert=True)
        return

    # Data format: toggle_{target_chat_id}_{key}
    parts = callback.data.split("_")
    # parts[0] = toggle
    # parts[1] = target_chat_id
    # parts[2:] = key (might contain underscores?)
    
    target_chat_id = int(parts[1])
    key = "_".join(parts[2:])

    new_state = await SettingsService.toggle_setting(target_chat_id, key)
    
    # Update UI
    settings = await SettingsService.get_all_settings(target_chat_id)
    kb = get_settings_keyboard(settings, target_chat_id)
    
    try:
        await callback.message.edit_reply_markup(reply_markup=kb)
    except Exception:
        pass # Not modified
        
    await callback.answer(f"{key} set to {new_state}")

@router.callback_query(F.data == "close_admin")
async def on_close(callback: CallbackQuery):
    await callback.message.delete()

@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    if str(message.from_user.id) not in os.getenv("ADMIN_IDS", "").split(","):
        return

    async with async_session() as session:
        result = await session.execute(select(ManagedGroup))
        groups = result.scalars().all()
    
    if not groups:
        await message.answer("⚠️ No groups managed. Use `/addgroup <id>` to add one.")
        return

    if len(groups) == 1:
        target_id = groups[0].chat_id
        group_name = groups[0].name or str(target_id)
        is_active = await SettingsService.get_setting(target_id, "broadcast_active")
        kb = get_broadcast_keyboard(is_active, target_id)
        await message.answer(f"📡 **Broadcaster Dashboard**\nGroup: **{group_name}**\nManage automated links here:", reply_markup=kb)
    else:
        # We need a group selection keyboard for broadcast specifically
        builder = InlineKeyboardBuilder()
        for g in groups:
            builder.button(text=g.name or str(g.chat_id), callback_data=f"bc_select_group_{g.chat_id}")
        builder.adjust(1)
        await message.answer("Please select a group for Broadcaster:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("bc_toggle_"))
async def on_bc_toggle(callback: CallbackQuery):
    target_id = int(callback.data.split("_")[2])
    new_state = await SettingsService.toggle_setting(target_id, "broadcast_active")
    
    is_active = new_state == "true"
    await callback.message.edit_reply_markup(reply_markup=get_broadcast_keyboard(is_active, target_id))
    await callback.answer(f"Broadcaster {'started' if is_active else 'stopped'}")

@router.callback_query(F.data.startswith("bc_stat_"))
async def on_bc_status(callback: CallbackQuery):
    target_id = int(callback.data.split("_")[2])
    async with async_session() as session:
        # Count pending for this specific chat
        res_pending = await session.execute(
            select(func.count(BroadcastQueue.id))
            .where(BroadcastQueue.sent == 0, BroadcastQueue.chat_id == target_id)
        )
        pending_count = res_pending.scalar()

        # Count sent for this specific chat
        res_sent = await session.execute(
            select(func.count(BroadcastQueue.id))
            .where(BroadcastQueue.sent == 1, BroadcastQueue.chat_id == target_id)
        )
        sent_count = res_sent.scalar()

        is_active = await SettingsService.get_setting(target_id, "broadcast_active")
        current_interval = await SettingsService.get_setting_str(target_id, "broadcast_interval", "60")

    status_icon = "🟢" if is_active else "🔴"
    text = (
        f"📊 **Broadcaster Status:**\n\n"
        f"State: {status_icon} {'Active' if is_active else 'Inactive'}\n"
        f"📥 **Pending**: {pending_count} links\n"
        f"📤 **Total Sent**: {sent_count} links\n"
        f"⏱ **Interval**: {current_interval}s"
    )
    await callback.message.answer(text)
    await callback.answer()

@router.callback_query(F.data.startswith("bc_add_"))
async def on_bc_add_link(callback: CallbackQuery, state: FSMContext):
    target_id = int(callback.data.split("_")[2])
    await state.set_state(BroadcastStates.waiting_for_link)
    await state.update_data(target_id=target_id)
    await callback.message.answer(f"🔗 [Group {target_id}]\nSend me the **link(s)** to add to the queue:")
    await callback.answer()

@router.message(BroadcastStates.waiting_for_link)
async def process_bc_link(message: Message, state: FSMContext):
    data = await state.get_data()
    target_id = data.get("target_id")
    if not target_id:
        await message.answer("⚠️ Error: Target group lost. Please start over.")
        await state.clear()
        return

    # Split by whitespace or newlines to get all potential links
    raw_links = message.text.split()
    input_links = [l.strip() for l in raw_links if l.strip().startswith("http")]

    if not input_links:
        await message.answer("❌ No valid links found. Please send a message containing valid URLs (starting with http).")
        return

    added_count = 0
    duplicate_count = 0
    
    async with async_session() as session:
        for link in input_links:
            # Duplicate check PER CHAT
            res = await session.execute(
                select(BroadcastQueue)
                .where(BroadcastQueue.link == link, BroadcastQueue.chat_id == target_id)
            )
            if res.scalars().first():
                duplicate_count += 1
                continue
            
            new_item = BroadcastQueue(link=link, chat_id=target_id)
            session.add(new_item)
            added_count += 1
        
        await session.commit()
    
    response = f"✅ [Group {target_id}] Successfully added **{added_count}** new links to the queue."
    if duplicate_count > 0:
        response += f"\n⚠️ Ignored **{duplicate_count}** duplicates already in this group's list."
        
    await message.answer(response)
    await state.clear()

@router.callback_query(F.data.startswith("bc_int_"))
async def on_bc_set_interval(callback: CallbackQuery, state: FSMContext):
    target_id = int(callback.data.split("_")[2])
    await state.set_state(BroadcastStates.waiting_for_interval)
    await state.update_data(target_id=target_id)
    await callback.message.answer(f"⏱ [Group {target_id}]\nSend me the **interval** in seconds (min 10s):")
    await callback.answer()

@router.message(BroadcastStates.waiting_for_interval)
async def process_bc_interval(message: Message, state: FSMContext):
    data = await state.get_data()
    target_id = data.get("target_id")
    if not target_id:
        await message.answer("⚠️ Error: Target group lost. Please start over.")
        await state.clear()
        return

    try:
        val = int(message.text.strip())
        if val < 10:
            await message.answer("❌ Minimum 10 seconds.")
            return
    except ValueError:
        await message.answer("❌ Please send a valid number.")
        return

    await SettingsService.set_setting(target_id, "broadcast_interval", str(val))
    
    await message.answer(f"✅ [Group {target_id}] Interval updated to **{val}s**")
    await state.clear()

@router.message(Command("help"))
async def cmd_help(message: Message):
    if str(message.from_user.id) not in os.getenv("ADMIN_IDS", "").split(","):
        return

    help_text = (
        "📖 **Available Admin Commands:**\n\n"
        "**Group Management:**\n"
        "• `/admin` - Dashboard: Toggle features, edit Welcome (Text, Image, Link, **Button Text**).\n"
        "• `/addgroup <id>` - Add a group (e.g., `-100...`)\n"
        "• `/delgroup <id>` - Remove a group\n"
        "• `/mygroups` - List managed groups\n\n"
        "**Welcome Placeholders:**\n"
        "• `{user}` - Tag/Mention the user\n"
        "• `{group}` - Name of the group\n\n"
        "**Broadcaster / Scheduler:**\n"
        "• `/broadcast` - Open the centralized dashboard (Add links, set interval, Toggle Start/Stop)\n\n"
        "**Other:**\n"
        "• `/help` - Show this message"
    )
    await message.answer(help_text)

# --- Expiring Message Handlers ---
import asyncio

@router.callback_query(F.data.startswith("timed_msg_"))
async def on_timed_msg_start(callback: CallbackQuery, state: FSMContext):
    if str(callback.from_user.id) not in os.getenv("ADMIN_IDS", "").split(","):
        await callback.answer("⛔ Unauthorized", show_alert=True)
        return

    target_id = int(callback.data.split("_")[2])
    await state.update_data(target_id=target_id)
    await state.set_state(ExpiringMessageStates.waiting_for_text)
    
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    await callback.message.answer(f"⏳ [Group {target_id}]\nSend me the **message** you want to post (text, photo, or video):")
    await callback.answer()

@router.message(ExpiringMessageStates.waiting_for_text)
async def process_timed_msg_text(message: Message, state: FSMContext):
    # Store the message content
    content_type = "text"
    content = message.text
    
    if message.photo:
        content_type = "photo"
        content = message.photo[-1].file_id
        await state.update_data(caption=message.caption or "")
    elif message.video:
        content_type = "video"
        content = message.video.file_id
        await state.update_data(caption=message.caption or "")
    elif not message.text:
        await message.answer("⚠️ Please send text, a photo, or a video.")
        return
    
    await state.update_data(content_type=content_type, content=content)
    await state.set_state(ExpiringMessageStates.waiting_for_duration)
    
    await message.answer("⏱ Now send me the **duration in seconds** before the message expires (e.g., `30` for 30 seconds):")

@router.message(ExpiringMessageStates.waiting_for_duration)
async def process_timed_msg_duration(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    target_id = data.get("target_id")
    content_type = data.get("content_type")
    content = data.get("content")
    caption = data.get("caption", "")
    
    if not target_id or not content:
        await message.answer("⚠️ Error: Data lost. Please start over.")
        await state.clear()
        return
    
    try:
        duration = int(message.text.strip())
        if duration < 1:
            await message.answer("❌ Duration must be at least 1 second.")
            return
        if duration > 86400:  # 24 hours max
            await message.answer("❌ Maximum duration is 86400 seconds (24 hours).")
            return
    except ValueError:
        await message.answer("❌ Please send a valid number (seconds).")
        return
    
    # Send the message to the target group
    try:
        if content_type == "text":
            sent_msg = await bot.send_message(chat_id=target_id, text=content, parse_mode="HTML")
        elif content_type == "photo":
            sent_msg = await bot.send_photo(chat_id=target_id, photo=content, caption=caption, parse_mode="HTML")
        elif content_type == "video":
            sent_msg = await bot.send_video(chat_id=target_id, video=content, caption=caption, parse_mode="HTML")
        else:
            await message.answer("❌ Unknown content type.")
            await state.clear()
            return
    except Exception as e:
        await message.answer(f"❌ Failed to send message: {e}")
        await state.clear()
        return
    
    await message.answer(f"✅ Message sent to group `{target_id}`. It will be deleted in **{duration} seconds**.")
    await state.clear()
    
    # Schedule deletion
    async def delete_after_delay():
        await asyncio.sleep(duration)
        try:
            await sent_msg.delete()
        except Exception:
            pass
    
    asyncio.create_task(delete_after_delay())
