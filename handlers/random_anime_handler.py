import random
from aiogram import Router, types
from mal import Anime
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from utils import select_random_anime_from_collected, load_collected_anime_data

router = Router()


@router.message(lambda message: message.text == "Показать рандомное аниме")
async def show_random_anime(message: types.Message):
    anime_list = load_collected_anime_data()
    anime_info = select_random_anime_from_collected(anime_list)
    reply_markup = InlineKeyboardBuilder()
    reply_markup.add(types.InlineKeyboardButton(text="Оценить", callback_data=f"rate_anime:{anime_info['id']}"))
    reply_markup.add(types.InlineKeyboardButton(text="Следующее", callback_data="next"))
    reply_markup.add(types.InlineKeyboardButton(text="Скрыть", callback_data="hide"))
    reply_markup.adjust(2, 1)
    if anime_info:
        await message.answer_photo(
            photo=anime_info["photo"],  # Отправляем изображение
            caption=anime_info["info"],  # Описание аниме
            parse_mode="HTML",
            reply_markup = reply_markup.as_markup()
        )
    else:
        await message.answer("Извините, не удалось найти аниме.", reply_markup=types.ReplyKeyboardRemove())

