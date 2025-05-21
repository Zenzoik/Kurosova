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

    await add_or_update_rating(query.from_user.id, mal_anime_id, rating)


    key = mal_key_builder(None, mal_anime_id)
    await caches.get('default').delete(key)

    await query.message.edit_text(f"Ви оцінили на {rating}/10")
    await query.answer()
