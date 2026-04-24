from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Извлекает текущего пользователя из JWT токена в куках.

    :param request: FastAPI Request объект
    :param db: Асинхронная сессия SQLAlchemy
    :return: Объект User
    :raises HTTPException: При отсутствии токена, его невалидности или отсутствии пользователя
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Неверный токен")
        
    result = await db.execute(select(User).where(User.email == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

async def require_admin(user: User = Depends(get_current_user)):
    """
    Проверяет, что текущий пользователь является администратором.

    :param user: Объект пользователя (извлекается автоматически)
    :return: Объект пользователя, если он админ
    :raises HTTPException: Если пользователь не админ
    """
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    return user