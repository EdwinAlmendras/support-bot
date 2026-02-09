from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_settings_keyboard(settings: dict, target_chat_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # Define mapping
    labels = {
        "delete_links": "🚫 Delete Links",
        "delete_joins": "👋 Delete Joins",
        "welcome_enabled": "✨ Welcome Message"
    }
    
    for key, label in labels.items():
        val = settings.get(key, "false").lower() == "true"
        status = "✅" if val else "❌"
        builder.button(
            text=f"{label}: {status}",
            callback_data=f"toggle_{target_chat_id}_{key}"
        )

    # Edit Buttons
    builder.button(text="✏️ Edit Welcome Text", callback_data=f"edit_welcome_{target_chat_id}_welcome_text")
    builder.button(text="🖼️ Edit Welcome Image", callback_data=f"edit_welcome_{target_chat_id}_welcome_image")
    builder.button(text="🔗 Edit Group Link", callback_data=f"edit_welcome_{target_chat_id}_welcome_link")
    builder.button(text="🔘 Edit Button Text", callback_data=f"edit_welcome_{target_chat_id}_welcome_button_text")
    builder.button(text="👁️ Preview Welcome", callback_data=f"preview_welcome_{target_chat_id}")
    builder.button(text="⏳ Send Expiring Message", callback_data=f"timed_msg_{target_chat_id}")
    builder.button(text="❌ Close / Cerrar", callback_data="close_admin")
    
    builder.adjust(1)
    return builder.as_markup()

def get_group_selection_keyboard(groups: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for g in groups:
        # Expecting objects with chat_id and name
        label = g.name if g.name else str(g.chat_id)
        builder.button(text=f"👥 {label}", callback_data=f"select_group_{g.chat_id}")
    builder.adjust(1)
    builder.button(text="❌ Close", callback_data="close_admin")
    return builder.as_markup()
