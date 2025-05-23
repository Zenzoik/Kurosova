import aiosqlite
import asyncio
from contextlib import asynccontextmanager
import logging

from aiocache import caches

from bot.config import DB_PATH
_db_connection = None
_db_connection_lock = asyncio.Lock()
logger = logging.getLogger(__name__)

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                user_id INTEGER,
                mal_anime_id INTEGER,
                user_rating INTEGER,
                PRIMARY KEY (user_id, mal_anime_id)
            );
        ''')
        await db.execute(
            'CREATE INDEX IF NOT EXISTS idx_ratings_user ON ratings(user_id);'
        )
        await db.commit()


@asynccontextmanager
async def get_db_connection():
    """Асинхронный контекстный менеджер для получения соединения с БД"""
    global _db_connection

    async with _db_connection_lock:
        if _db_connection is None:
            _db_connection = await aiosqlite.connect(DB_PATH)

    try:
        yield _db_connection
    except Exception as e:
        logger.error(f"Помилка під час роботи с БД: {e}")
        raise


async def add_or_update_rating(user_id:int, mal_anime_id:int, user_rating:int):
    async with get_db_connection() as db:
        await db.execute(
            '''
            INSERT INTO ratings (user_id, mal_anime_id, user_rating)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, mal_anime_id)
            DO UPDATE SET user_rating = excluded.user_rating
            ''',
            (user_id, mal_anime_id, user_rating)
        )
        await db.commit()
        
async def get_user_ratings(user_id: int, offset: int = 0, limit: int = 5):
    """Получение всех оценённых аниме пользователя с поддержкой пагинации"""
    async with get_db_connection() as db:
        cursor = await db.execute(
            "SELECT mal_anime_id, user_rating FROM ratings WHERE user_id = ? LIMIT ? OFFSET ?",
            (user_id, limit, offset)
        )
        rows = await cursor.fetchall()

    return {row[0]: row[1] for row in rows}


async def get_user_rating_info(mal_anime_id):
    """Получение информации о рейтинге аниме"""
    async with get_db_connection() as db:
        async with db.execute("SELECT AVG(user_rating), COUNT(user_rating) FROM ratings WHERE mal_anime_id = ?", (mal_anime_id,)) as cursor:
            result = await cursor.fetchone()
            return {"avg_rating": result[0], "rating_count": result[1]} if result else None

async def get_user_rating_for_anime(user_id: int, mal_anime_id: int):
    async with get_db_connection() as db:
        async with db.execute(
            "SELECT user_rating FROM ratings WHERE user_id = ? AND mal_anime_id = ?",
            (user_id, mal_anime_id)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def delete_user_rating(user_id: int, mal_anime_id: int):
    async with get_db_connection() as db:
        await db.execute(
            "DELETE FROM ratings WHERE user_id = ? AND mal_anime_id = ?",
            (user_id, mal_anime_id)
        )
        await db.commit()
        await caches.get("default").delete(f"mal:{mal_anime_id}")
