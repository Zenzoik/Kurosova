from aiogram import Router, types
from bot.services.database import add_or_update_rating
from aiocache import caches
from bot.utils.utils import mal_key_builder

router = Router()

@router.callback_query(lambda c: c.data.startswith("rate:"))
async def handle_rating(query: types.CallbackQuery):
    print(f"DEBUG: query.data = {query.data}")
    _, mal_anime_id, rating = query.data.split(":")
    mal_anime_id = int(mal_anime_id)
    rating = int(rating)

    # 1) сохранение/обновление оценки в БД
    await add_or_update_rating(query.from_user.id, mal_anime_id, rating)

    # 2) инвалидируем кэш для этого MAL ID

    key = mal_key_builder(None, mal_anime_id)
    await caches.get('default').delete(key)

    await add_or_update_rating(query.from_user.id, int(mal_anime_id), int(rating))
    await query.message.edit_text(f"Вы оценил на {rating}/10")
    await query.answer()
