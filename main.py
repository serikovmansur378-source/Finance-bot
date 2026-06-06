import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers import start, expenses
from handlers.debts import router as debts_router
from handlers.reset import router as reset_router

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()


    dp.include_router(start.router)
    dp.include_router(reset_router)
    dp.include_router(expenses.router)
    dp.include_router(debts_router)

    print("The bot is working!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())