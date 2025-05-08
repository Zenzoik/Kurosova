import asyncio
import logging
from bot.config import BOT_TOKEN, LOG_LEVEL, REDIS_DSN
from bot.utils.logger import setup as setup_logging
from bot.utils.cache import init_cache
import sys
from aiogram import Bot, Dispatcher

from bot.services.database import init_db
from bot.handlers import(start_handler,
                         inline_search_my,
                         inline_search,
                         random_anime_handler,
                         query_handler,
                         anime_rating)

setup_logging(LOG_LEVEL)
logger = logging.getLogger(__name__)
init_cache(REDIS_DSN)
# Создание экземпляра бота
bot = Bot(BOT_TOKEN)

# Настройка диспетчера
dp = Dispatcher()

# Регистрация роутеров обработчиков
# Порядок важен: более специфичные обработчики должны быть выше
dp.include_router(anime_rating.router)
dp.include_router(random_anime_handler.router)
dp.include_router(query_handler.router)
dp.include_router(inline_search_my.router)
dp.include_router(inline_search.router)
dp.include_router(start_handler.router)

async def main():
    """
    Основная функция запуска бота
    """
    try:
        logger.info("Запуск бота...")
        
        # Инициализация базы данных
        await init_db()
        logger.info("База данных инициализирована")
        
        # Удаление вебхука и очистка очереди обновлений
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Запуск поллинга
        logger.info("Бот запущен и ожидает сообщений")
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске бота: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
    except Exception as e:
        logger.critical(f"Необработанное исключение: {e}")