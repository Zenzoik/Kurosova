import logging
import json
import os
from mal import Anime
import random
from aiogram.utils.markdown import hide_link
from database import get_user_rating_info

# Настройка логирования
logger = logging.getLogger(__name__)

# Константа для пути к файлу данных
ANIME_DATA_FILE = 'anime_data_filtered.json'

async def get_anime_info_by_mal_id(mal_id):
    """
    Получает информацию об аниме по его MAL ID
    
    Args:
        mal_id: ID аниме на MyAnimeList
        
    Returns:
        dict: Словарь с информацией об аниме или None в случае ошибки
    """
    try:
        anime = Anime(mal_id)
        if anime.title is None:
            logger.error(f"Аниме с MAL ID {mal_id} не найдено.")
            return None

        # Получаем среднюю оценку пользователей и количество оценок из базы данных
        user_rating_info = await get_user_rating_info(mal_id)
        if not user_rating_info:
            user_rating_info = {"avg_rating": 0, "rating_count": 0}

        anime_info = {
            'mal_id': mal_id,
            'title': anime.title,
            'image_url': anime.image_url,
            'score': anime.score,
            'type': anime.type,
            'episodes': anime.episodes,
            'synopsis': anime.synopsis,
            'user_avg_rating': user_rating_info.get('avg_rating', 0),
            'user_rating_count': user_rating_info.get('rating_count', 0)
        }

        # Следующий комментарий указывает на то, что здесь можно добавить кэширование
        # в будущем для оптимизации запросов к API
        # add_to_cache(mal_id, anime_info)
        
        return anime_info
    except Exception as e:
        logger.error(f"Ошибка при запросе к MAL API для MAL ID {mal_id}: {e}")
        return None

def load_collected_anime_data():
    """
    Загружает данные об аниме из JSON-файла
    
    Returns:
        list: Список аниме из файла или пустой список в случае ошибки
    """
    try:
        if not os.path.exists(ANIME_DATA_FILE):
            logger.error(f"Файл {ANIME_DATA_FILE} не найден")
            return []
            
        with open(ANIME_DATA_FILE, 'r', encoding='utf-8') as file:
            anime_list = json.load(file)
        return anime_list
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных об аниме: {e}")
        return []

def check_attributes(anime):
    """
    Проверяет наличие необходимых атрибутов у объекта аниме
    
    Args:
        anime: Объект аниме для проверки
        
    Returns:
        list: Список отсутствующих атрибутов
    """
    attributes_to_check = ['title', 'scored_by', 'type', 'episodes', 'score', 'image_url']
    missing_attributes = []
    for attr in attributes_to_check:
        if getattr(anime, attr, None) is None:
            missing_attributes.append(attr)
    return missing_attributes

def select_random_anime_from_collected(anime_list):
    """
    Выбирает случайное аниме из списка и форматирует информацию
    
    Args:
        anime_list: Список аниме для выбора
        
    Returns:
        dict: Информация о выбранном аниме
    """
    if not anime_list:
        logger.error("Список аниме пуст, невозможно выбрать случайное аниме")
        return None
        
    try:
        random_anime = random.choice(anime_list)
        anime_info = (
            f"🖊 Название: {random_anime['title']}\n"
            f"🖥 Тип: {random_anime['type']}\n"
            f"🗃 Эпизоды: {random_anime['episodes']}\n"
            f"⭐️ Оценка на MAL: {random_anime['score']}\n"
            f"🤙 Количество оценок: {random_anime['scored_by']}\n"
            f"{hide_link(random_anime['image_url'])}"
        )
        return {
            "info": anime_info,
            "id": random_anime['id'],
            "photo": random_anime['image_url'],
            "title": random_anime['title']
        }
    except Exception as e:
        logger.error(f"Ошибка при выборе случайного аниме: {e}")
        return None
