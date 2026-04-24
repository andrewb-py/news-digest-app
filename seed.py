# seed.py
import asyncio
from sqlalchemy import select
from app.database import async_session
from app.models.topic import Topic


async def seed_topics():
    async with async_session() as session:
        result = await session.execute(
            select(Topic).where(Topic.slug.in_(["tech", "science", "business"]))
        )
        existing = result.scalars().all()
        if existing:
            print("Темы уже существуют:", [t.name for t in existing])
            return

        topics = [
            Topic(name='Технологии', slug='tech'),
            Topic(name='Наука', slug='science'),
            Topic(name='Бизнес', slug='business')
        ]
        session.add_all(topics)
        await session.commit()
        print('Темы успешно добавлены в базу данных.')


if __name__ == "__main__":
    asyncio.run(seed_topics())