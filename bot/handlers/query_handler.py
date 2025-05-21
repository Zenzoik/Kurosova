from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.services.database import delete_user_rating
from bot.services.keyboards import get_rating_keyboard
from bot.utils.utils import select_random_anime_from_collected, load_collected_anime_data

router = Router()

@router.callback_query(F.data.startswith('rate_anime'))
async def handle_rating(query: types.CallbackQuery):
    mal_anime_id = query.data.split(':')[1]
    await query.bot.send_message(query.from_user.id, text="Виберіть оцінку від 0 до 10:", reply_markup=get_rating_keyboard(mal_anime_id))
    await query.answer()

@router.callback_query(F.data.startswith("next"))
async def handle_next(query: types.CallbackQuery):
    anime_list = load_collected_anime_data()

    anime_info = select_random_anime_from_collected(anime_list)
    reply_markup = InlineKeyboardBuilder()
    reply_markup.add(types.InlineKeyboardButton(text="Оцінити", callback_data=f"rate_anime:{anime_info['id']}"))
    reply_markup.add(types.InlineKeyboardButton(text="Наступне", callback_data="next"))
    reply_markup.add(types.InlineKeyboardButton(text="Сховати", callback_data="hide"))
    reply_markup.adjust(2, 1)

    if anime_info:
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
        await query.message.edit_text("Пробачте, не вдалося знайти аніме.")
    try:
        await query.answer()
    except TelegramBadRequest:
        pass


@router.callback_query(F.data == "hide")
async def handle_hide(query: types.CallbackQuery):
    try:
        await query.message.delete()
        await query.answer()
    except TelegramBadRequest:
        pass

@router.callback_query(F.data.startswith("del_anime:"))
async def handle_delete(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    mal_id  = int(callback.data.split(":")[1])

    await delete_user_rating(user_id, mal_id)
    try:
        await callback.bot.edit_message_reply_markup(
            inline_message_id=callback.inline_message_id,
            reply_markup=None,
        )
    except TelegramBadRequest:
        pass

    await callback.answer("Оцінку видалено", show_alert=False)

