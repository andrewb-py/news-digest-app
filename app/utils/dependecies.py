from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    """! 
    Извлекает текущего пользователя из JWT-токена в куках.
    
    @param request FastAPI Request объект
    @param db Асинхронная сессия SQLAlchemy
    @return Объект User, если токен валиден и пользователь существует
    @exception HTTPException При отсутствии токена, его невалидности или отсутствии пользователя (401, 404)
    """
    token = request.cookies.get("access_token")
    if not token: raise HTTPException(status_code=401, detail="Не авторизован")
    
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Неверный токен")
        
    result = await db.execute(select(User).where(User.email == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user: raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

async def require_admin(user: User = Depends(get_current_user)):
    """! 
    Проверяет, является ли пользователь администратором.
    
    @param user Объект User (обычно полученный через get_current_user)
    @return Объект User, если роль администратор
    @exception HTTPException При отсутствии прав администратора (403)
    """
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    return user