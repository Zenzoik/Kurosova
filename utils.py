import logging
from database import get_user_rating_info
import json
from mal import Anime
import random
from aiogram.utils.markdown import hide_link

async def get_anime_info_by_mal_id(mal_id):
    # # Попытка получить данные из кэша
    # cached_data = get_from_cache(mal_id)
    # if cached_data:
    #     logging.info(f"Используем кэшированные данные для MAL ID: {mal_id}")
    #     return cached_data

    # Если данных нет в кэше, делаем запрос к MAL и базе данных
    try:
        anime = Anime(mal_id)
        if anime.title is None:
            logging.error(f"Аниме с MAL ID {mal_id} не найдено.")
            return None

        # Получаем среднюю оценку пользователей и количество оценок из базы данных
        user_rating_info = await get_user_rating_info(mal_id)

        anime_info = {
            'mal_id': mal_id,
            'title': anime.title,
            'image_url': anime.image_url,
            'score': anime.score,
            'type': anime.type,
            'episodes': anime.episodes,
            'synopsis': anime.synopsis,
            'user_avg_rating': user_rating_info.get('avg_rating', 0),  # Средняя оценка пользователей
            'user_rating_count': user_rating_info.get('rating_count', 0)  # Количество оценок пользователей
        }

        # Добавляем полученную информацию в кэш с отметкой времени
        # add_to_cache(mal_id, anime_info)
        return anime_info
    except Exception as e:
        logging.error(f"Ошибка при запросе к MAL API для MAL ID {mal_id}: {e}")
        return None

def load_collected_anime_data():
    with open('anime_data_filtered.json', 'r') as file:
        anime_list = json.load(file)
    return anime_list


def check_attributes(anime):
    attributes_to_check = ['title', 'scored_by', 'type', 'episodes', 'score', 'image_url']
    missing_attributes = []
    for attr in attributes_to_check:
        if getattr(anime, attr, None) is None:
            missing_attributes.append(attr)
    return missing_attributes

def load_collected_anime_data():
    with open('anime_data_filtered.json', 'r') as file:
        anime_list = json.load(file)
    return anime_list

def select_random_anime_from_collected(anime_list):
    random_anime = random.choice(anime_list)
    anime_info = f"🖊 Название: {random_anime['title']}\n 🖥 Тип: {random_anime['type']}\n 🗃 Эпизоды: {random_anime['episodes']}\n ⭐️ Оценка на MAL: {random_anime['score']}\n 🤙 Количество оценок: {random_anime['scored_by']}\n {hide_link(random_anime['image_url'])}"
    return {"info": anime_info, "id": random_anime['id'], "photo": random_anime['image_url'], "title": random_anime['title']}
