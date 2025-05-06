import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from config import API_TOKEN, LOGGING_LEVEL
from database import init_db
from handlers import (
    anime_rating, 
    random_anime_handler, 
    start_handler, 
    inline_search, 
    inline_search_my, 
    query_handler
)

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOGGING_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)

logger = logging.getLogger(__name__)

# Создание экземпляра бота
bot = Bot(API_TOKEN)

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