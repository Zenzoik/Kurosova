from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_rating_keyboard(mal_anime_id):
    builder = InlineKeyboardBuilder()
    for i in range(11):
        builder.button(text=f"{i}", callback_data=f"rate:{mal_anime_id}:{i}")
    builder.adjust(1, 3, 3, 3)
    return builder.as_markup()

def get_rating_my_keyboard(mal_id):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Переоцінити", callback_data=f"rate_anime:{mal_id}",))
    kb.add(InlineKeyboardButton(text="🗑 Видалити",callback_data=f"del_anime:{mal_id}"))
    return kb.as_markup()

def get_rate_anime_keyboard(mal_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Оцінити", callback_data=f"rate_anime:{mal_id}"))
    return builder.as_markup()

def get_random_anime_inline_keyboard(anime_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Оцінити", callback_data=f"rate:{anime_id}"))
    builder.add(InlineKeyboardButton(text="Наступне", callback_data=f"next"))
    builder.add(InlineKeyboardButton(text="Сховати", callback_data="hide"))
    builder.adjust(2,1)
    return builder.as_markup()

def get_random_anime_keyboard():
    button_random_anime = KeyboardButton(text = 'Показати рандомне аніме')
    keyboard_random_anime = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[button_random_anime]])
    return keyboard_random_anime
