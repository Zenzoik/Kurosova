import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import API_TOKEN
from database import init_db
from handlers import anime_rating, random_anime_handler, start_handler, inline_search, inline_search_my, query_handler
logging.basicConfig(level=logging.INFO)

bot = Bot(API_TOKEN)

dp = Dispatcher()
dp.include_router(anime_rating.router)
dp.include_router(random_anime_handler.router)
dp.include_router(query_handler.router)
dp.include_router(inline_search_my.router)
dp.include_router(inline_search.router)
dp.include_router(start_handler.router)

async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())