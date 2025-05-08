import os
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

LOG_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("DB_PATH", ROOT_DIR / "anime_ratings.db"))
REDIS_DSN = os.getenv("REDIS_DSN", "localhost:6379")