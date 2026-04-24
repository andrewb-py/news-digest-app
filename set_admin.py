import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from app.database import async_session
from app.models.user import User

async def make_admin(email: str):
    async with async_session() as db:
        result = await db.execute(update(User).where(User.email == email).values(role="admin"))
        await db.commit()
        if result.rowcount > 0:
            print(f"Пользователь {email} теперь администратор.")
        else:
            print(f"Пользователь с email {email} не найден.")

if __name__ == "__main__":
    email = input("Введите email пользователя: ").strip()
    asyncio.run(make_admin(email))