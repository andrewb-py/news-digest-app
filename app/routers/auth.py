from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserSettings
from app.schemas.auth import UserRegister, UserLogin
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    """
    Отображает форму регистрации.

    :param request: FastAPI Request объект
    :return: HTML-страница с формой
    """
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@router.post("/register", response_class=HTMLResponse)
async def register(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Обрабатывает форму регистрации нового пользователя.

    Валидирует email (уникальность) и сложность пароля.
    При успехе создаёт запись в БД, генерирует JWT и перенаправляет в личный кабинет.

    :param request: FastAPI Request объект с формой
    :param db: Асинхронная сессия SQLAlchemy
    :return: RedirectResponse на /dashboard или HTML с ошибками
    """
    form = await request.form()
    email, password = form.get("email"), form.get("password")
    
    if not email or not password:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Заполните все поля"})
        
    # Проверка уникальности
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        return templates.TemplateResponse("register.html", {"request": request, "error": "Email уже зарегистрирован"})
        
    # Валидация сложности (дублируем логику схемы для форм)
    try:
        UserRegister(email=email, password=password)
    except ValueError as e:
        return templates.TemplateResponse("register.html", {"request": request, "error": str(e)})
        
    user = User(email=email, hashed_password=hash_password(password), role="user")
    db.add(user)
    await db.flush()
    db.add(UserSettings(user_id=user.id, email_notifications=True))
    await db.commit()
    
    token = create_access_token({"sub": email, "role": "user"})
    resp = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    resp.set_cookie("access_token", token, httponly=True, max_age=604800)
    return resp

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    """
    Отображает форму входа.

    :param request: FastAPI Request объект
    :return: HTML-страница с формой входа
    """
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Обрабатывает форму входа.

    Проверяет email и пароль. При успехе генерирует JWT и перенаправляет в кабинет.

    :param request: FastAPI Request объект с формой
    :param db: Асинхронная сессия SQLAlchemy
    :return: RedirectResponse на /dashboard или HTML с ошибкой
    """
    form = await request.form()
    email, password = form.get("email"), form.get("password")
    
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный email или пароль"})
        
    token = create_access_token({"sub": email, "role": user.role})
    resp = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    resp.set_cookie("access_token", token, httponly=True, max_age=604800)
    return resp

@router.post("/logout")
async def logout():
    """
    Выходит из аккаунта, удаляя JWT-токен из куки.

    :return: RedirectResponse на страницу входа
    """
    resp = RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    resp.delete_cookie("access_token")
    return resp