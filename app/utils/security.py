from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import get_settings
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()

def verify_password(plain: str, hashed: str) -> bool:
    """! 
    Проверяет соответствие пароля и его хэша.
    
    @param plain Открытый пароль
    @param hashed Хэш пароля (bcrypt)
    @return True, если пароль верен
    """
    return pwd_context.verify(plain, hashed)

def hash_password(password: str) -> str:
    """! 
    Хэширует пароль с использованием bcrypt.
    
    @param password Пароль в открытом виде
    @return Хэш пароля
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires: timedelta = None) -> str:
    """! 
    Создаёт JWT токен доступа.
    
    @param data Полезная нагрузка (обычно {"sub": "user_email"})
    @param expires Срок действия токена
    @return Закодированный JWT токен
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires or timedelta(days=7))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    """! 
    Декодирует JWT токен.
    
    @param token JWT строка
    @return Полезная нагрузка, если токен валиден, иначе None
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None