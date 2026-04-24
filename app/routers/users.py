from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database import get_db
from app.models.user import User, UserSettings
from app.models.topic import Topic, UserTopic
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/settings", response_class=HTMLResponse)
async def settings(request: Request, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """! 
    Отображает страницу настроек профиля пользователя.
    
    Показывает текущие настройки уведомлений и выбранные темы.
    
    @param request FastAPI Request объект
    @param db Асинхронная сессия SQLAlchemy
    @param user Текущий пользователь (авторизован)
    @return HTML-страница с формами настроек
    """
    settings = (await db.execute(select(UserSettings).where(UserSettings.user_id == user.id))).scalar_one()
    all_topics = (await db.execute(select(Topic))).scalars().all()
    user_topic_ids = {r for r in (await db.execute(select(UserTopic.topic_id).where(UserTopic.user_id == user.id))).scalars().all()}
    
    msg = request.query_params.get("msg")
    return templates.TemplateResponse("settings.html", {
        "request": request, "user": user, "settings": settings,
        "topics": all_topics, "user_topic_ids": user_topic_ids, "msg": msg
    })

@router.post("/settings/topics")
async def save_topics(request: Request, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """! 
    Сохраняет выбранные пользователем темы.
    
    Перезаписывает связи UserTopic в БД.
    
    @param request FastAPI Request объект с формой
    @param db Асинхронная сессия SQLAlchemy
    @param user Те��ущий пользователь (авторизован)
    @return RedirectResponse с сообщением об успехе
    """
    form = await request.form()
    selected_slugs = form.getlist("topics")
    
    topics = (await db.execute(select(Topic).where(Topic.slug.in_(selected_slugs)))).scalars().all()
    topic_ids = {t.id for t in topics}
    
    await db.execute(delete(UserTopic).where(UserTopic.user_id == user.id))
    for tid in topic_ids:
        db.add(UserTopic(user_id=user.id, topic_id=tid))
    await db.commit()
    
    return RedirectResponse(url="/profile/settings?msg=Настройки+сохранены", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/settings/notifications")
async def save_notifications(request: Request, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """! 
    Сохраняет настройку уведомлений пользователя.
    
    @param request FastAPI Request объект с формой
    @param db Асинхронная сессия SQLAlchemy
    @param user Текущий пользователь (авторизован)
    @return RedirectResponse с сообщением об успехе
    """
    form = await request.form()
    enable = form.get("email_notifications") == "on"
    
    settings = (await db.execute(select(UserSettings).where(UserSettings.user_id == user.id))).scalar_one()
    settings.email_notifications = enable
    await db.commit()
    
    return RedirectResponse(url="/profile/settings?msg=Настройки+сохранены", status_code=status.HTTP_303_SEE_OTHER)