from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    """Главное меню с 5 кнопками"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное", callback_data="main")],
        [InlineKeyboardButton(text="📖 О проекте", callback_data="about")],
        [InlineKeyboardButton(text="👥 Участники", callback_data="participants")],
        [InlineKeyboardButton(text="📰 Журнал", callback_data="journal")],
        [InlineKeyboardButton(text="🔗 Ресурсы", callback_data="resources")]
    ])

def back_button():
    """Кнопка 'Назад' — возвращает в главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ])
