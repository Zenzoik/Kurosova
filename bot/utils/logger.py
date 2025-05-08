import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent / "bot.log"

def setup(level: str = "INFO") -> None:
    """
    Настраивает корневой логгер:
      • выводит в консоль (stdout) — удобно в Docker и systemd-journal
      • пишет в файл bot.log с ротацией до 5×2 МБ
    """
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    handlers = [
        logging.StreamHandler(),                              # → консоль
        RotatingFileHandler(LOG_FILE, maxBytes=2_097_152,     # 2 МБ
                            backupCount=5, encoding="utf-8")  # 5 архивов
    ]

    logging.basicConfig(
        level=level.upper(),
        format=fmt,
        datefmt=datefmt,
        handlers=handlers,
    )

    # Понижаем шум от aiogram и aiohttp до WARNING
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
