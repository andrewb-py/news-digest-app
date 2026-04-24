from fastapi import APIRouter, Depends, Request, Query, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.user import User
from app.models.news import NewsItem, Favorite, news_topics
from app.models.topic import UserTopic
from app.utils.dependencies import get_current_user, require_admin
from app.services.recommendation_service import get_recommended_news

router = APIRouter(prefix="/news", tags=["news"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/feed", response_class=HTMLResponse)
async def news_feed(request: Request, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """! 
    Отображает ленту новостей с рекомендациями для пользователя.
    
    @param request FastAPI Request объект
    @param db Асинхронная сессия SQLAlchemy
    @param user Текущий пользователь (авторизован)
    @return HTML-страница с лентой новостей
    """
    # Теперь лента сортируется по рекомендациям
    news = await get_recommended_news(db, user.id)
    fav_ids = set((await db.execute(select(Favorite.news_id).where(Favorite.user_id == user.id))).scalars().all())
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "news": news, "user": user, 
        "favorites": fav_ids, "msg": request.query_params.get("status")
    })

@router.get("/search", response_class=HTMLResponse)
async def search_news(request: Request, q: str = Query(None), db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """! 
    Выполняет поиск новостей по заголовку или саммари.
    
    @param request FastAPI Request объект
    @param q Поисковый запрос
    @param db Асинхронная сессия SQLAlchemy
    @param user Текущий пользователь (авторизован)
    @return HTML-страница с результатами поиска
    """
    if not q or len(q.strip()) < 2:
        return templates.TemplateResponse("dashboard.html", {"request": request, "news": [], "user": user, "favorites": set(), "search_query": q, "error": "Введите минимум 2 символа"})
    
    q = q.strip()
    query = select(NewsItem).where(
        NewsItem.status == "published",
        or_(NewsItem.title.ilike(f"%{q}%"), NewsItem.summary.ilike(f"%{q}%"))
    ).order_by(NewsItem.published_at.desc())
    
    news = (await db.execute(query.options(selectinload(NewsItem.topics)))).scalars().all()
    fav_ids = set((await db.execute(select(Favorite.news_id).where(Favorite.user_id == user.id))).scalars().all())
    
    return templates.TemplateResponse("dashboard.html", {"request": request, "news": news, "user": user, "favorites": fav_ids, "search_query": q})

@router.post("/{news_id}/favorite")
async def toggle_favorite(news_id: int, request: Request, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """! 
    Добавляет или удаляет новость из избранного пользователя.
    
    @param news_id ID новости
    @param request FastAPI Request объект
    @param db Асинхронная сессия SQLAlchemy
    @param user Текущий пользователь (авторизован)
    @return RedirectResponse на предыдущую страницу
    """
    existing = (await db.execute(select(Favorite).where(Favorite.user_id == user.id, Favorite.news_id == news_id))).scalar_one_or_none()
    if existing: await db.delete(existing)
    else: db.add(Favorite(user_id=user.id, news_id=news_id))
    await db.commit()
    return RedirectResponse(url=request.headers.get("referer", "/news/feed"), status_code=status.HTTP_303_SEE_OTHER)

@router.get("/favorites", response_class=HTMLResponse)
async def user_favorites(request: Request, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """! 
    Отображает страницу избранных новостей пользователя.
    
    @param request FastAPI Request объект
    @param db Асинхронная сессия SQLAlchemy
    @param user Текущий пользователь (авторизован)
    @return HTML-страница со списком избранных новостей
    """
    fav_ids = (await db.execute(
        select(Favorite.news_id).where(Favorite.user_id == user.id)
    )).scalars().all()

    news = []
    if fav_ids:
        news = (await db.execute(
            select(NewsItem).where(NewsItem.id.in_(fav_ids)).order_by(NewsItem.published_at.desc()).options(selectinload(NewsItem.topics))
        )).scalars().all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request, "news": news, "user": user, 
        "favorites": set(fav_ids), "is_fav_page": True
    })

@router.post("/{news_id}/delete")
async def delete_news(news_id: int, request: Request, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    """! 
    Удаляет новость из базы данных (только для администраторов).
    
    @param news_id ID новости для удаления
    @param request FastAPI Request объект
    @param db Асинхронная сессия SQLAlchemy
    @param admin Администратор (авторизован)
    @return RedirectResponse на предыдущую страницу
    """
    news = (await db.execute(select(NewsItem).where(NewsItem.id == news_id))).scalar_one_or_none()
    if news:
        await db.delete(news)  # Каскадно удалит связи (избранное и т.д.)
        await db.commit()
    return RedirectResponse(url=request.headers.get("referer", "/news/feed"), status_code=status.HTTP_303_SEE_OTHER)