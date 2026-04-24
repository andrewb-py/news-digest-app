from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.news import NewsItem
from app.models.topic import UserTopic

async def get_recommended_news(db, user_id: int, limit: int = 20):
    """
    Возвращает рекомендованные новости для пользователя на основе его интересов.

    :param db: Асинхронная сессия SQLAlchemy
    :param user_id: ID пользователя
    :param limit: Максимальное количество новостей
    :return: Список объектов NewsItem, отсортированных по релевантности
    """
    user_topic_ids = set((await db.execute(
        select(UserTopic.topic_id).where(UserTopic.user_id == user_id)
    )).scalars().all())

    news_items = (await db.execute(
        select(NewsItem)
        .where(NewsItem.status == "published")
        .options(selectinload(NewsItem.topics))
        .order_by(NewsItem.published_at.desc())
    )).scalars().all()

    scored = []
    for item in news_items:
        item_topic_ids = {t.id for t in item.topics}
        score = len(item_topic_ids.intersection(user_topic_ids)) * 10
        scored.append((score, item))
        
    scored.sort(key=lambda x: (-x[0], x[1].published_at))
    return [item for _, item in scored[:limit]]