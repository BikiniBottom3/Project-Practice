import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database import *
from keyboards import *
from states import AddHabitStates

logging.basicConfig(level=logging.INFO)

# 👇👇👇 ВСТАВЬ СВОЙ ТОКЕН 👇👇👇
BOT_TOKEN = "8573310292:AAEyeLa1rEzPFQLdmb9Qd8vOFeh9JhmC8n8"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ========== СТАРТ ==========
@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    add_user(user_id, username, full_name)

    await message.answer(
        f"Привет, {full_name}! 👋\n\n"
        "Я бот-трекер привычек.\n"
        "Добавляй привычки, отмечай их выполнение и следи за стриками!\n\n"
        "👇 Нажми на кнопку, чтобы начать 👇",
        reply_markup=main_menu()
    )


# ========== МОИ ПРИВЫЧКИ ==========
@dp.callback_query(lambda c: c.data == "my_habits")
async def show_habits(callback: CallbackQuery):
    habits = get_habits(callback.from_user.id)

    if not habits:
        await callback.message.edit_text(
            "📋 У вас пока нет привычек.\n\n"
            "Нажмите «➕ Добавить привычку», чтобы создать первую!",
            reply_markup=main_menu()
        )
        return

    text = "📋 *Ваши привычки:*\n\n"
    for habit_id, name, description, reminder_time in habits:
        streak = get_streak(habit_id)

        # Смайлик для стрика
        if streak == 0:
            streak_emoji = "⚪️"
        elif streak < 3:
            streak_emoji = "🟢"
        elif streak < 7:
            streak_emoji = "🔵"
        else:
            streak_emoji = "🔥"

        text += f"{streak_emoji} *{name}*\n"
        text += f"   📝 {description}\n"
        if reminder_time:
            text += f"   ⏰ Напоминание: {reminder_time}\n"
        text += f"   📅 Стрик: {streak} дней\n\n"

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=habits_list(habits))


# ========== СТАТИСТИКА ==========
@dp.callback_query(lambda c: c.data == "stats")
async def show_stats(callback: CallbackQuery):
    habits = get_habits(callback.from_user.id)

    if not habits:
        await callback.message.edit_text(
            "📊 У вас пока нет привычек.\n\n"
            "Добавьте первую привычку, чтобы видеть статистику!",
            reply_markup=main_menu()
        )
        return

    text = "📊 *Ваша статистика*\n\n"
    total_streak = 0
    streaks = []

    for habit_id, name, description, reminder_time in habits:
        streak = get_streak(habit_id)
        total_streak += streak
        streaks.append(streak)

        # Выбираем смайлик
        if streak == 0:
            emoji = "⚪️"
        elif streak < 3:
            emoji = "🟢"
        elif streak < 7:
            emoji = "🔵"
        elif streak < 14:
            emoji = "🟣"
        elif streak < 30:
            emoji = "⭐️"
        else:
            emoji = "👑"

        text += f"{emoji} *{name}*: {streak} дн.\n"
        if reminder_time:
            text += f"   ⏰ {reminder_time}\n"

    best_streak = max(streaks) if streaks else 0

    text += f"\n✨ *Общий стрик:* {total_streak} дней"
    text += f"\n🏆 *Рекорд:* {best_streak} дней"

    # Мотивационная фраза
    if total_streak == 0:
        text += "\n\n💪 Начни сегодня — и завтра будет первый день!"
    elif total_streak < 7:
        text += "\n\n🌟 Ты только начинаешь! Продолжай в том же духе!"
    elif total_streak < 30:
        text += "\n\n🎉 Отлично! Ты на правильном пути!"
    else:
        text += "\n\n🏆 Ты легенда! Так держать!"

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=main_menu())


# ========== ПОМОЩЬ ==========
@dp.callback_query(lambda c: c.data == "help")
async def show_help(callback: CallbackQuery):
    help_text = """
❓ *Помощь по боту*

📌 *Как пользоваться:*
1️⃣ Нажми «➕ Добавить привычку»
2️⃣ Введи название и описание
3️⃣ Укажи время напоминания (или напиши «пропустить»)
4️⃣ В меню «📋 Мои привычки» отмечай выполнение ✅
5️⃣ Следи за прогрессом в «📊 Моя статистика»

🔥 *Что такое стрик?*
Стрик — это количество дней ПОДРЯД, когда ты выполнял привычку.
Пропустил день? Стрик обнуляется!

⏰ *Напоминания*
Бот пришлёт уведомление в указанное время.
Не забудь отметить выполнение!

📊 *Статистика*
Показывает:
• Текущий стрик по каждой привычке
• Общий стрик (сумма всех дней)
• Личный рекорд

💡 *Совет*
Начни с 1-2 привычек. Когда войдёшь в ритм — добавляй новые!

"""
    await callback.message.edit_text(help_text, parse_mode="Markdown", reply_markup=main_menu())


# ========== ДОБАВЛЕНИЕ ПРИВЫЧКИ ==========
@dp.callback_query(lambda c: c.data == "add_habit")
async def start_add_habit(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddHabitStates.waiting_for_name)
    await callback.message.edit_text(
        "📝 *Добавление привычки*\n\n"
        "Введите название привычки.\n"
        "Например: «Пить воду», «Зарядка», «Читать книгу»\n\n"
        "Отменить добавление: /cancel",
        parse_mode="Markdown"
    )


@dp.message(Command("cancel"))
async def cancel_add_habit(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Добавление привычки отменено", reply_markup=main_menu())


@dp.message(AddHabitStates.waiting_for_name)
async def get_habit_name(message: Message, state: FSMContext):
    if message.text.startswith("/"):
        await message.answer("❌ Отменено")
        await state.clear()
        return

    await state.update_data(name=message.text)
    await state.set_state(AddHabitStates.waiting_for_description)
    await message.answer(
        "✍️ *Описание*\n\n"
        "Теперь введите описание привычки.\n"
        "Например: «Выпивать стакан воды после пробуждения»",
        parse_mode="Markdown"
    )


@dp.message(AddHabitStates.waiting_for_description)
async def get_habit_description(message: Message, state: FSMContext):
    if message.text.startswith("/"):
        await message.answer("❌ Отменено")
        await state.clear()
        return

    await state.update_data(description=message.text)
    await state.set_state(AddHabitStates.waiting_for_reminder_time)
    await message.answer(
        "⏰ *Время напоминания*\n\n"
        "Введите время в формате ЧЧ:ММ (например, 09:00)\n"
        "Если не хотите напоминание, напишите: `пропустить`",
        parse_mode="Markdown"
    )


@dp.message(AddHabitStates.waiting_for_reminder_time)
async def get_reminder_time(message: Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data['name']
    description = user_data['description']

    reminder_time = None
    if message.text.lower() != "пропустить":
        try:
            datetime.strptime(message.text, "%H:%M")
            reminder_time = message.text
        except ValueError:
            await message.answer(
                "❌ Неверный формат!\n\n"
                "Введите время как ЧЧ:ММ (например, 14:30)\n"
                "Или напишите «пропустить»"
            )
            return

    add_habit(message.from_user.id, name, description, reminder_time)
    await state.clear()

    result_text = f"✅ Привычка *{name}* успешно добавлена!\n\n"
    result_text += f"📝 {description}\n"
    if reminder_time:
        result_text += f"⏰ Напоминание в {reminder_time}\n"
    result_text += "\nНе забывай отмечать выполнение в меню «Мои привычки»!"

    await message.answer(result_text, parse_mode="Markdown", reply_markup=main_menu())


# ========== ОТМЕТКА ВЫПОЛНЕНИЯ ==========
@dp.callback_query(lambda c: c.data.startswith("check_"))
async def check_habit_callback(callback: CallbackQuery):
    habit_id = int(callback.data.split("_")[1])

    # Проверяем, есть ли такая привычка
    habit = get_habit_by_id(habit_id)
    if not habit:
        await callback.answer("❌ Привычка не найдена!", show_alert=True)
        return

    success = check_habit(habit_id)
    streak = get_streak(habit_id)
    habit_name = habit[1]

    if success:
        if streak == 1:
            message = f"✅ {habit_name} отмечено! 🎉\nНачинается новый стрик!"
        elif streak % 7 == 0:
            message = f"✅ {habit_name} отмечено! 🔥\n{streak} дней подряд! Ты красавчик!"
        else:
            message = f"✅ {habit_name} отмечено! 🔥 Стрик: {streak} дней"
        await callback.answer(message, show_alert=True)
    else:
        await callback.answer(f"⚠️ {habit_name} уже отмечено сегодня!", show_alert=True)

    # Обновляем отображение привычек
    await show_habits(callback)


# ========== НАЗАД ==========
@dp.callback_query(lambda c: c.data == "back")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏠 *Главное меню*\n\n"
        "Выбери действие:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )


# ========== ЗАПУСК ==========
async def main():
    init_db()
    print("🤖 Бот запущен!")
    print("✅ Статистика и помощь активны!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
