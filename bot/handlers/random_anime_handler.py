from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.utils import select_random_anime_from_collected, load_collected_anime_data

router = Router()


@router.message(lambda message: message.text == "Показати рандомне аніме")
async def show_random_anime(message: types.Message):
    anime_list = load_collected_anime_data()
    anime_info = select_random_anime_from_collected(anime_list)
    reply_markup = InlineKeyboardBuilder()
    reply_markup.add(types.InlineKeyboardButton(text="Оцінить", callback_data=f"rate_anime:{anime_info['id']}"))
    reply_markup.add(types.InlineKeyboardButton(text="Наступне", callback_data="next"))
    reply_markup.add(types.InlineKeyboardButton(text="Сховати", callback_data="hide"))
    reply_markup.adjust(2, 1)
    if anime_info:
        await message.answer_photo(
            photo=anime_info["photo"],  # Отправляем изображение
            caption=anime_info["info"],  # Описание аниме
            parse_mode="HTML",
            reply_markup = reply_markup.as_markup()
        )
    else:
        await message.answer("Вибачте, не вдалося знайти аніме.", reply_markup=types.ReplyKeyboardRemove())

