import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database import get_habits_with_reminder
from bot import bot

logging.basicConfig(level=logging.INFO)

async def send_reminders():
    now = datetime.now().strftime("%H:%M")
    habits = get_habits_with_reminder(now)
    for user_id, habit_id, habit_name in habits:
        try:
            await bot.send_message(
                user_id,
                f"⏰ *Напоминание!*\n\nНе забудь выполнить: *{habit_name}*",
                parse_mode="Markdown"
            )
            print(f"Напоминание отправлено: {habit_name}")
        except:
            pass

async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_reminders, 'cron', minute='*')
    scheduler.start()
    print("⏰ Планировщик напоминаний запущен!")
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
