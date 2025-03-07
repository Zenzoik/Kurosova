import os
from aiogram import Bot
from dotenv import load_dotenv
load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(API_TOKEN)
