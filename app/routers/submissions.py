from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.news import NewsSubmission
from app.models.topic import Topic
from app.utils.dependencies import get_current_user
from app.utils.validators import is_url_accessible
from app.services.parser_service import fetch_web_content
from app.services.llm_service import generate_news_data

router = APIRouter(prefix="/submit", tags=["submissions"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def submit_form(request: Request, user: User = Depends(get_current_user)):
    """
    Отображает форму подачи новой новости.

    :param request: FastAPI Request объект
    :param user: Текущий пользователь (авторизован)
    :return: HTML-страница с формой
    """
    return templates.TemplateResponse("submit.html", {"request": request, "user": user, "error": None})

@router.post("/", response_class=HTMLResponse)
async def submit_news(request: Request, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Обрабатывает отправку новой новости на модерацию.

    Извлекает текст из URL или комментария, генерирует метаданные через LLM.

    :param request: FastAPI Request объект с формой
    :param db: Асинхронная сессия SQLAlchemy
    :param user: Текущий пользователь (авторизован)
    :return: RedirectResponse на ленту с сообщением
    """
    form = await request.form()
    url, comment = form.get("url"), form.get("comment")
    
    if not await is_url_accessible(url):
        return templates.TemplateResponse("submit.html", {"request": request, "user": user, "error": "Ссылка недоступна"})
    
    submission = NewsSubmission(user_id=user.id, url=url, comment=comment, status="pending")
    
    all_slugs = (await db.execute(select(Topic.slug))).scalars().all()
    try:
        text = await fetch_web_content(url) if url else comment
        submission.llm_data = await generate_news_data(text or "Нет текста", url or "manual", all_slugs)
    except Exception as e:
        submission.llm_data = {"title": "На модерации", "summary": str(e), "topics": []}
        
    db.add(submission)
    await db.commit()
    
    return RedirectResponse(url="/news/feed?status=Заявка+отправлена+на+модерацию", status_code=status.HTTP_303_SEE_OTHER)