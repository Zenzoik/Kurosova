from aiogram import Router, types
from bot.services.database import add_or_update_rating

router = Router()

@router.callback_query(lambda c: c.data.startswith("rate:"))
async def handle_rating(query: types.CallbackQuery):
    print(f"DEBUG: query.data = {query.data}")
    _, mal_anime_id, rating, = query.data.split(":")
    await add_or_update_rating(query.from_user.id, int(mal_anime_id), int(rating))
    await query.message.edit_text(f"Вы оценил на {rating}/10")
    await query.answer()
