from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

def get_rating_keyboard(mal_anime_id):
    builder = InlineKeyboardBuilder()
    for i in range(11):
        builder.button(text=f"{i}", callback_data=f"rate:{mal_anime_id}:{i}")
    builder.adjust(1, 3, 3, 3)
    return builder.as_markup()

def get_random_anime_inline_keyboard(anime_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Оценить", callback_data=f"rate:{anime_id}"))
    builder.add(InlineKeyboardButton(text="Следующее", callback_data=f"next"))
    builder.add(InlineKeyboardButton(text="Скрыть", callback_data="hide"))
    builder.adjust(2,1)
    return builder.as_markup()

def get_random_anime_keyboard():
    button_random_anime = KeyboardButton(text = 'Показать рандомное аниме')
    keyboard_random_anime = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[button_random_anime]])
    return keyboard_random_anime
