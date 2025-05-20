from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.services.keyboards import get_random_anime_keyboard


router = Router()
@router.message(Command('start'))
async def start_message(message: Message):
    await message.answer("Привіт, я допоможу тобі шукати аніме\n Використовуй @anime_rate_bot 'твій запит' для пошуку бажаного аніме\n Використовуй @anime_rate_bot 'my' для відображення оціненних аніме",reply_markup=get_random_anime_keyboard())