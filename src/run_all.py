import asyncio
import threading
from bot import main as bot_main
from reminders import main as reminders_main


async def run_bot():
    await bot_main()


def run_reminders():
    asyncio.run(reminders_main())


if __name__ == "__main__":
    # Запускаем бота в основном потоке
    bot_thread = threading.Thread(target=lambda: asyncio.run(bot_main()))
    bot_thread.start()

    # Запускаем напоминания в другом потоке
    reminders_thread = threading.Thread(target=run_reminders)
    reminders_thread.start()

    # Ждём завершения (никогда не завершится)
    bot_thread.join()
    reminders_thread.join()
