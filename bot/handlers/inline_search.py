from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, LinkPreviewOptions
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from mal import AnimeSearch
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
            search_results = AnimeSearch("Darling in the FranXX").results[:5]
        else:
            search_results = AnimeSearch(search_query).results[:5]  # Получаем первые 5 результатов
    except ValueError:
        # MAL вернул «0 results» — просто скажем Telegram-у, что нечего показать
        logging.info(f"⛔ Ничего не найдено по запросу «{search_query}»")
        return await inline_query.answer([], is_personal=True)
    articles = []
    for anime in search_results:
        # Проверяем, является ли anime словарем (кэшированные данные) или объектом (данные из API)
        mal_id = anime['mal_id'] if isinstance(anime, dict) else anime.mal_id
        user_rating = await get_user_rating_for_anime(user_id, int(mal_id))
        user_rating_text = f"⭐️ Ваша оценка: {user_rating}" if user_rating is not None else ""

        title = anime['title'] if isinstance(anime, dict) else anime.title
        description = f"{anime['score']}\n{anime['type']}" if isinstance(anime, dict) else f"{anime.score}\n{anime.type}"
        thumb_url = anime['image_url'] if isinstance(anime, dict) else anime.image_url
        episodes = anime['episodes'] if isinstance(anime, dict) else anime.episodes
        score = anime['score'] if isinstance(anime, dict) else anime.score

        input_content = InputTextMessageContent(
            message_text=f"🖊 Название: {title}\n"
                         f"🖥 Тип: {anime['type'] if isinstance(anime, dict) else anime.type}\n"
                         f"🗃 Эпизоды: {episodes}\n"
                         f"⭐️ Оценка на MAL: {score}\n"
                         f"{user_rating_text}\n"
                         "\u2800", #костыль, невидимый символ для адекватного размещения превью и текста

            parse_mode='HTML',
            link_preview_options=LinkPreviewOptions(
                url=thumb_url,
                prefer_small_media=True,
                show_above_text=False
            )
        )
        reply_markup = None
        if chat_type_check == "sender":
            reply_markup = InlineKeyboardBuilder()
            reply_markup.add(types.InlineKeyboardButton(text="Оценить", callback_data=f"rate_anime:{mal_id}"))
            reply_markup = reply_markup.as_markup()
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