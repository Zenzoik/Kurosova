from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, LinkPreviewOptions
import asyncio
from mal import AnimeSearch

from bot.services.keyboards import get_rate_anime_keyboard
from bot.utils.logger import logging

from bot.services.database import get_user_rating_for_anime

router = Router()

@router.inline_query()
async def anime_search(inline_query: InlineQuery):
    user_id = inline_query.from_user.id
    search_query = inline_query.query.strip() or "Darling in the FranXX"  # По умолчанию для примера
    chat_type_check = inline_query.chat_type

    try:
        if not search_query or search_query == "Darling in the FranXX":
            search_results = await asyncio.to_thread(
                lambda: AnimeSearch("Darling in the FranXX").results[:5]
            )
        else:
            search_results = await asyncio.to_thread(
                lambda: AnimeSearch(search_query).results[:5]
            )
    except ValueError:
        logging.info(f"⛔ Нічого не знайдено по запиту «{search_query}»")
        return await inline_query.answer([], is_personal=True)
    articles = []
    for anime in search_results:
        mal_id = anime['mal_id'] if isinstance(anime, dict) else anime.mal_id
        user_rating = await get_user_rating_for_anime(user_id, int(mal_id))
        user_rating_text = f"⭐️ Ваша оцінка: {user_rating}" if user_rating is not None else ""

        title = anime['title'] if isinstance(anime, dict) else anime.title
        description = f"{anime['score']}\n{anime['type']}" if isinstance(anime, dict) else f"{anime.score}\n{anime.type}"
        thumb_url = anime['image_url'] if isinstance(anime, dict) else anime.image_url
        episodes = anime['episodes'] if isinstance(anime, dict) else anime.episodes
        score = anime['score'] if isinstance(anime, dict) else anime.score

        input_content = InputTextMessageContent(
            message_text=f"🖊 Назва: {title}\n"
                         f"🖥 Тип: {anime['type'] if isinstance(anime, dict) else anime.type}\n"
                         f"🗃 Епізоди: {episodes}\n"
                         f"⭐️ Оцінка на MAL: {score}\n"
                         f"{user_rating_text}\n"
                         "\u2800",

            parse_mode='HTML',
            link_preview_options=LinkPreviewOptions(
                url=thumb_url,
                prefer_small_media=True,
                show_above_text=False
            )
        )
        reply_markup = None
        if chat_type_check == "sender":
            reply_markup = get_rate_anime_keyboard(mal_id)
        article = InlineQueryResultArticle(
            id=str(mal_id),
            title=title,
            description=description,
            input_message_content=input_content,
            thumb_url=thumb_url,
            reply_markup=reply_markup
        )
        articles.append(article)
        # photo = InlineQueryResultPhoto(
        #     id = str(mal_id),
        #     title = title,
        #     description = description,
        #     photo_url = thumb_url,
        #     caption = f"🖊 Название: {title}\n"
        #                  f"🖥 Тип: {anime['type'] if isinstance(anime, dict) else anime.type}\n"
        #                  f"🗃 Эпизоды: {episodes}\n"
        #                  f"⭐️ Оценка на MAL: {score}\n"
        #                  f"{user_rating_text}\n",
        #     parse_mode = 'HTML',
        #     thumbnail_url = thumb_url,
        #     reply_markup = reply_markup
        # )
        # articles.append(photo)

    await inline_query.answer(articles, is_personal=True, cache_time=0)