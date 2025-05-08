from bot.utils.utils import get_anime_info_by_mal_id
from bot.services.database import get_user_ratings
import logging
import asyncio
from aiogram import Router, types
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, LinkPreviewOptions
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.inline_query(lambda query: query.query == "my")
async def show_user_rated_anime(inline_query: InlineQuery):
    """Показывает аниме, оценённые пользователем"""
    
    offset = int(inline_query.offset) if inline_query.offset else 0
    user_id = inline_query.from_user.id

    logging.info("Вызван show_user_rated_anime")

    # Загружаем данные из БД (оценки пользователя)
    user_ratings = await get_user_ratings(user_id, offset, 5)

    if not user_ratings:
        logging.info(f"Для пользователя с ID {user_id} нет оцененных аниме.")
        return await inline_query.answer([], is_personal=True, cache_time=0)

    # **Параллельное выполнение запросов для ускорения**
    tasks = [get_anime_info_by_mal_id(mal_id) for mal_id in user_ratings.keys()]
    anime_infos = await asyncio.gather(*tasks, return_exceptions=True)

    # Формируем результаты
    articles = []
    for anime_info, (mal_id, rating) in zip(anime_infos, user_ratings.items()):
        if isinstance(anime_info, Exception):
            logging.error(f"Ошибка при запросе к MAL API для MAL ID {mal_id}: {anime_info}")
            continue

        if not anime_info:
            logging.error(f"Информация по MAL ID {mal_id} не найдена.")
            continue

        title = anime_info['title']
        thumb_url = anime_info['image_url']
        score = anime_info['score']

        input_content = InputTextMessageContent(
            message_text=f"🖊 Название: {title}\n"
                         f"⭐️ Оценка на MAL: {score}\n"
                         f"⭐️ Ваша оценка: {rating}\n"
                         f"📊 Средняя оценка пользователей бота: {anime_info.get('user_avg_rating', 'Нет оценок')}\n"
                         f"👥 Количество оценок пользователей бота: {anime_info.get('user_rating_count', 0)}\n"
                         "\u2800",
            parse_mode='HTML',
            link_preview_options=LinkPreviewOptions(
                url=thumb_url,
                prefer_small_media=True,
                show_above_text=False
            )
        )

        reply_markup = None
        if inline_query.chat_type == "sender":
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text="Переоценить", callback_data=f"rate_anime:{mal_id}"))
            reply_markup = builder.as_markup()

        article = InlineQueryResultArticle(
            id=str(mal_id),
            title=title,
            description=f"Ваша оценка: {rating}",
            input_message_content=input_content,
            thumb_url=thumb_url,
            reply_markup=reply_markup
        )
        articles.append(article)

    # Если загружено 5 аниме, добавляем `next_offset` для загрузки следующих
    next_offset = str(offset + 5) if len(user_ratings) == 5 else ""

    await inline_query.answer(articles, is_personal=True, cache_time=0, next_offset=next_offset)
