from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_settings_keyboard(settings: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # Define mapping
    labels = {
        "delete_links": "🚫 Delete Links",
        "delete_joins": "👋 Delete Joins"
    }
    
    for key, label in labels.items():
        val = settings.get(key, "false").lower() == "true"
        status = "✅" if val else "❌"
        builder.button(
            text=f"{label}: {status}",
            callback_data=f"toggle_{key}"
        )

    # Edit Buttons
    builder.button(text="✏️ Edit Welcome Text", callback_data="edit_welcome_welcome_text")
    builder.button(text="🖼️ Edit Welcome Image", callback_data="edit_welcome_welcome_image")
    builder.button(text="🔗 Edit Group Link", callback_data="edit_welcome_welcome_link")
    
    builder.adjust(1)
    return builder.as_markup()
