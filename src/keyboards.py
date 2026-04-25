from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Мои привычки", callback_data="my_habits")],
        [InlineKeyboardButton(text="➕ Добавить привычку", callback_data="add_habit")],
        [InlineKeyboardButton(text="📊 Моя статистика", callback_data="stats")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
    ])

def habits_list(habits):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for habit_id, name, description, reminder_time in habits:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"✅ {name}",
                callback_data=f"check_{habit_id}"
            )
        ])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back")])
    return keyboard
