import aiosqlite

DB_PATH = "anime_ratings.db"

async def init_db():
    """Инициализация базы данных"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                user_id INTEGER,
                mal_anime_id INTEGER,
                user_rating INTEGER,
                PRIMARY KEY (user_id, mal_anime_id)
            )
        ''')
        await db.commit()

async def add_or_update_rating(user_id, mal_anime_id, user_rating):
    """Добавление или обновление оценки пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO ratings (user_id, mal_anime_id, user_rating)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, mal_anime_id)
            DO UPDATE SET user_rating = excluded.user_rating
        ''', (user_id, mal_anime_id, user_rating))
        await db.commit()
        
async def get_user_ratings(user_id: int, offset: int = 0, limit: int = 5):
    """Получение всех оценённых аниме пользователя с поддержкой пагинации"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT mal_anime_id, user_rating FROM ratings WHERE user_id = ? LIMIT ? OFFSET ?",
            (user_id, limit, offset)
        )
        rows = await cursor.fetchall()

    # Преобразуем в словарь {mal_anime_id: user_rating}
    return {row[0]: row[1] for row in rows}


async def get_user_rating_info(mal_anime_id):
    """Получение информации о рейтинге аниме"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT AVG(user_rating), COUNT(user_rating) FROM ratings WHERE mal_anime_id = ?", (mal_anime_id,)) as cursor:
            result = await cursor.fetchone()
            return {"average": result[0], "count": result[1]} if result else None

async def get_user_rating_for_anime(user_id: int, mal_anime_id: int):
    async with aiosqlite.connect("anime_ratings.db") as db:
        # Выполнение запроса к базе данных для поиска оценки пользователя
        async with db.execute("""
            SELECT user_rating FROM ratings
            WHERE user_id = ? AND mal_anime_id = ?
        """, (user_id, mal_anime_id)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]  # Возвращаем оценку пользователя, если она найдена
    return None  # Возвращаем None, если оценка не найдена