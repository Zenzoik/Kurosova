from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from keyboards import get_random_anime_keyboard


router = Router()
@router.message(Command('start'))
async def start_message(message: Message):
    user_id = message.from_user.id  # Telegram User ID
    tg_tag = message.from_user.username
    chat_id = message.chat.id  # Chat ID может отличаться от User ID в групповых чатах или каналах
    await message.answer("Привіт, я допоможу тобі шукати аніме",reply_markup=get_random_anime_keyboard())