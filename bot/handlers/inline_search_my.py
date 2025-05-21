# bot/handlers/inline_search_my.py
from bot.services.keyboards import get_rating_my_keyboard
from bot.utils.utils import get_anime_info_by_mal_id
from bot.services.database import (
    get_user_ratings,
    get_user_rating_info,
)
import asyncio, logging
from aiogram import Router, types
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    LinkPreviewOptions,
)


router = Router()


@router.inline_query(lambda q: q.query == "my")
async def show_user_rated_anime(inline_query: InlineQuery) -> None:
    """Отдаёт список аниме, которые пользователь уже оценил."""

    offset = int(inline_query.offset or 0)
    user_id = inline_query.from_user.id
    logging.info("Вызван show_user_rated_anime")

    user_ratings = await get_user_ratings(user_id, offset, 5)

    if not user_ratings:
        await inline_query.answer([], is_personal=True, cache_time=0)
        return

    mal_ids = list(user_ratings.keys())

    anime_infos, stats = await asyncio.gather(
        asyncio.gather(*(get_anime_info_by_mal_id(mid) for mid in mal_ids),
                       return_exceptions=True),
        asyncio.gather(*(get_user_rating_info(mid) for mid in mal_ids))
    )

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
            f"🖊 Назва: {title}\n"
            f"⭐️ Оцінка на MAL: {mal_score}\n"
            f"⭐️ Ваша оцінка: {my_rating}\n"
            f"🎺 Середня оцінка користувачів бота: {avg:.1f}\n"
            f"👥 Кількість оцінок користувачів бота: {cnt}"
            "\u2800"
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

        reply_markup = None
        if inline_query.chat_type == "sender":
            reply_markup = get_rating_my_keyboard(mal_id)

        articles.append(
            InlineQueryResultArticle(
                id=str(mal_id),
                title=title,
                description=f"Ваша оцінка: {my_rating}",
                input_message_content=input_content,
                thumb_url=thumb_url,
                reply_markup=reply_markup,
            )
        )

    next_offset = str(offset + 5) if len(user_ratings) == 5 else ""

    await inline_query.answer(
        articles, is_personal=True, cache_time=0, next_offset=next_offset
    )
