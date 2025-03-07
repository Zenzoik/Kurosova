from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
from keyboards import get_rating_keyboard
from utils import select_random_anime_from_collected, load_collected_anime_data

router = Router()

@router.callback_query(F.data.startswith('rate_anime'))
async def handle_rating(query: types.CallbackQuery):
    mal_anime_id = query.data.split(':')[1]
    await query.bot.send_message(query.from_user.id, text="Choose rating from 0 to 10:", reply_markup=get_rating_keyboard(mal_anime_id))
    await query.answer()

@router.callback_query(F.data.startswith("next"))
async def handle_next(query: types.CallbackQuery):
    # Сначала обновляем сообщение, указывая, что поиск начался
    anime_list = load_collected_anime_data()

    # Запускаем функцию выбора следующего аниме из загруженного списка
    anime_info = select_random_anime_from_collected(anime_list)
    reply_markup = InlineKeyboardBuilder()
    reply_markup.add(types.InlineKeyboardButton(text="Оценить", callback_data=f"rate_anime:{anime_info['id']}"))
    reply_markup.add(types.InlineKeyboardButton(text="Следующее", callback_data="next"))
    reply_markup.add(types.InlineKeyboardButton(text="Скрыть", callback_data="hide"))
    reply_markup.adjust(2, 1)

    # Проверяем, удалось ли найти аниме
    if anime_info:
        # Если аниме найдено, обновляем сообщение с новым аниме
        await query.message.edit_media(
            media=types.InputMediaPhoto(media=anime_info["photo"]),
            reply_markup=reply_markup.as_markup(),
            parse_mode="HTML"
        )
        await query.message.edit_caption(
            caption=anime_info["info"],
            reply_markup=reply_markup.as_markup(),
            parse_mode="HTML"
        )
    else:
        await query.message.edit_text("Извините, не удалось найти аниме.")
    try:
        await query.answer()
    except TelegramBadRequest:
        pass  # Игнорируем ошибку, если callback query устарел


@router.callback_query(F.data == "hide")
async def handle_hide(query: types.CallbackQuery):
    try:
        await query.message.delete()
        await query.answer()
    except TelegramBadRequest:
        pass  # Игнорируем ошибку, если сообщение уже удалено или query устарел

