# bot/handlers/inline_search_my.py
from bot.utils.utils import get_anime_info_by_mal_id
from bot.services.database import (
    get_user_ratings,
    get_user_rating_info,
    get_user_rating_for_anime,
)
import asyncio, logging
from aiogram import Router, types
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    LinkPreviewOptions,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.inline_query(lambda q: q.query == "my")
async def show_user_rated_anime(inline_query: InlineQuery) -> None:
    """Отдаёт список аниме, которые пользователь уже оценил."""

    offset = int(inline_query.offset or 0)
    user_id = inline_query.from_user.id
    logging.info("Вызван show_user_rated_anime")

    # 1. Берём из БД максимум 5 записей начиная с offset
    user_ratings = await get_user_ratings(user_id, offset, 5)  # {mal_id: rating}

    if not user_ratings:
        await inline_query.answer([], is_personal=True, cache_time=0)
        return

    mal_ids = list(user_ratings.keys())

    # 2. Параллельно достаём MAL-данные и свежую статистику пользователей
    anime_infos, stats = await asyncio.gather(
        asyncio.gather(*(get_anime_info_by_mal_id(mid) for mid in mal_ids),
                       return_exceptions=True),
        asyncio.gather(*(get_user_rating_info(mid) for mid in mal_ids))
    )

    # 3. Формируем InlineQueryResultArticle-список
    articles: list[InlineQueryResultArticle] = []

    for mal_id, info, stat in zip(mal_ids, anime_infos, stats):
        if isinstance(info, Exception) or not info:
            logging.error(f"Ошибка MAL API для id={mal_id}: {info}")
            continue

        title      = info["title"]
        thumb_url  = info["image_url"]
        mal_score  = info["score"]
        my_rating  = user_ratings[mal_id]
        avg        = stat["avg_rating"] or 0
        cnt        = stat["rating_count"]

        text = (
            f"🖊 Название: {title}\n"
            f"⭐️ Оценка на MAL: {mal_score}\n"
            f"⭐️ Ваша оценка: {my_rating}\n"
            f"🎺 Средняя оценка пользователей бота: {avg:.1f}\n"
            f"👥 Количество оценок пользователей бота: {cnt}"
            "\u2800"          # невидимый символ, чтобы Telegram не урезал снизу
        )
        input_content = InputTextMessageContent(
            message_text=text,
            parse_mode="HTML",
            link_preview_options=LinkPreviewOptions(
                url=thumb_url,
                prefer_small_media=True,
                show_above_text=False,
            ),
        )

        # кнопка «Переоценить» показывается только в личном чате с ботом
        reply_markup = None
        if inline_query.chat_type == "sender":
            kb = InlineKeyboardBuilder()
            kb.add(types.InlineKeyboardButton(
                text="Переоценить",
                callback_data=f"rate_anime:{mal_id}",
            ))
            reply_markup = kb.as_markup()

        articles.append(
            InlineQueryResultArticle(
                id=str(mal_id),
                title=title,
                description=f"Ваша оценка: {my_rating}",
                input_message_content=input_content,
                thumb_url=thumb_url,
                reply_markup=reply_markup,
            )
        )

    # 4. next_offset для пагинации
    next_offset = str(offset + 5) if len(user_ratings) == 5 else ""

    await inline_query.answer(
        articles, is_personal=True, cache_time=0, next_offset=next_offset
    )
