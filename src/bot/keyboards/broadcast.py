from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_broadcast_keyboard(is_active: bool, target_chat_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # Status Toggle
    status_text = "🛑 Stop Broadcaster" if is_active else "🚀 Start Broadcaster"
    builder.button(text=status_text, callback_data=f"bc_toggle_{target_chat_id}")
    
    # Management Buttons
    builder.button(text="➕ Add Link", callback_data=f"bc_add_{target_chat_id}")
    builder.button(text="⏱ Set Interval", callback_data=f"bc_int_{target_chat_id}")
    builder.button(text="📊 Status & Queue", callback_data=f"bc_stat_{target_chat_id}")
    
    # Navigation
    builder.button(text="❌ Close / Cerrar", callback_data="close_admin")
    
    builder.adjust(1)
    return builder.as_markup()
