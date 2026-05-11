import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import BOT_TOKEN
from keyboards import main_menu, back_button
from texts import WELCOME, ABOUT_PROJECT, PARTICIPANTS, JOURNAL, RESOURCES

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Словарь для быстрого доступа к текстам по callback_data
CONTENT = {
    "main": WELCOME,
    "about": ABOUT_PROJECT,
    "participants": PARTICIPANTS,
    "journal": JOURNAL,
    "resources": RESOURCES,
}

# Команда /start — отправляем главное меню (новым сообщением)
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        WELCOME,
        parse_mode="Markdown",
        reply_markup=main_menu(),
        disable_web_page_preview=True
    )

# Обработка нажатий на кнопки меню
@dp.callback_query(lambda c: c.data in CONTENT)
async def send_info(callback: CallbackQuery):
    text = CONTENT[callback.data]
    # Отправляем НОВОЕ сообщение с текстом и кнопкой "Назад"
    await callback.message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=back_button(),
        disable_web_page_preview=True
    )
    # Убираем часики на кнопке (callback answer)
    await callback.answer()

# Обработка кнопки "Назад" — возвращаем главное меню
@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.answer(
        "🏠 *Главное меню*\n\nВыберите раздел:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )
    await callback.answer()

# Запуск
async def main():
    print("🤖 Бот для проекта запущен (режим новых сообщений)!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
