from fastapi import APIRouter, Depends, Request, status, Form, File, UploadFile, BackgroundTasks
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.news import NewsSubmission, NewsItem
from app.models.topic import Topic
from app.utils.dependencies import require_admin
from app.services.parser_service import fetch_web_content, extract_pdf_text
from app.services.llm_service import generate_news_data
from app.services.email_service import notify_users_about_new_news
from app.utils.validators import is_url_accessible
import os, shutil

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/moderation", response_class=HTMLResponse)
async def moderation_page(request: Request, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    """
    Отображает страницу модерации для администратора.

    :param request: FastAPI Request объект
    :param db: Асинхронная сессия SQLAlchemy
    :param admin: Администратор (авторизован)
    :return: HTML-страница со списком ожидающих модерации материалов
    """
    query = select(NewsSubmission).where(NewsSubmission.status == "pending").order_by(NewsSubmission.created_at.desc())
    subs = (await db.execute(query)).scalars().all()
    
    return templates.TemplateResponse("admin_moderation.html", {
        "request": request,
        "submissions": subs
    })

@router.post("/moderation/{sub_id}/approve")
async def approve_submission(
    sub_id: int,
    request: Request,
    bg_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    title: str = Form(None),
    summary: str = Form(None),
    topic_slugs: list[str] = Form(None)
):
    """
    Одобряет материал на модерации и публикует новость.

    :param sub_id: ID материала для модерации
    :param request: FastAPI Request объект
    :param bg_tasks: Фоновые задачи FastAPI
    :param db: Асинхронная сессия SQLAlchemy
    :param admin: Администратор (авторизован)
    :param title: Заголовок новости (может быть переопределен)
    :param summary: Саммари новости (может быть переопределено)
    :param topic_slugs: Список slug тем для новости
    :return: RedirectResponse на страницу модерации
    """
    sub = (await db.execute(select(NewsSubmission).where(NewsSubmission.id == sub_id))).scalar_one_or_none()
    if not sub:
        return RedirectResponse(url="/admin/moderation", status_code=status.HTTP_404_NOT_FOUND)

    llm_data = sub.llm_data or {}
    
    final_title = title.strip() if title else llm_data.get("title")
    final_summary = summary.strip() if summary else llm_data.get("summary")

    selected_slugs = topic_slugs if topic_slugs else llm_data.get("topics", [])
    topics = []
    if selected_slugs:
        topics = (await db.execute(select(Topic).where(Topic.slug.in_(selected_slugs)))).scalars().all()

    news = NewsItem(
        title=final_title,
        summary=final_summary,
        original_url=sub.url or "#",
        source_type="pdf" if sub.pdf_path else "web",
        status="published",
        topics=topics
    )
    db.add(news)

    sub.status = "approved"
    sub.reviewed_by = admin.id
    sub.reviewed_at = func.now()
    sub.news_item = news

    await db.commit()
    
    bg_tasks.add_task(notify_users_about_new_news, news.id)
    
    return RedirectResponse(url="/admin/moderation", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/moderation/{sub_id}/reject")
async def reject_submission(sub_id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    """
    Отклоняет материал на модерации.

    :param sub_id: ID материала для модерации
    :param db: Асинхронная сессия SQLAlchemy
    :param admin: Администратор (авторизован)
    :return: RedirectResponse на страницу модерации
    """
    sub = (await db.execute(select(NewsSubmission).where(NewsSubmission.id == sub_id))).scalar_one_or_none()
    if sub:
        sub.status = "rejected"
        sub.reviewed_by = admin.id
        await db.commit()
    return RedirectResponse(url="/admin/moderation", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/moderation/{sub_id}/delete")
async def delete_submission(sub_id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    """
    Удаляет материал на модерации.

    :param sub_id: ID материала для модерации
    :param db: Асинхронная сессия SQLAlchemy
    :param admin: Администратор (авторизован)
    :return: RedirectResponse на страницу модерации
    """
    sub = (await db.execute(select(NewsSubmission).where(NewsSubmission.id == sub_id))).scalar_one_or_none()
    if sub:
        await db.delete(sub)
        await db.commit()
    return RedirectResponse(url="/admin/moderation", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/add", response_class=HTMLResponse)
async def admin_add_form(
    request: Request, 
    url: str = Form(None), 
    file: UploadFile = File(None), 
    db: AsyncSession = Depends(get_db), 
    admin: User = Depends(require_admin)
):
    """
    Обрабатывает добавление материала администратором через URL или файл.

    :param request: FastAPI Request объект
    :param url: URL для парсинга (опционально)
    :param file: Загружаемый файл PDF (опционально)
    :param db: Асинхронная сессия SQLAlchemy
    :param admin: Администратор (авторизован)
    :return: RedirectResponse на страницу модерации
    """
    if url:
        if not await is_url_accessible(url):
            return templates.TemplateResponse("admin_add.html", {"request": request, "error": "URL недоступен"})
        try:
            text = await fetch_web_content(url)
            all_slugs = [t.slug for t in (await db.execute(select(Topic.slug))).scalars().all()]
            llm_data = await generate_news_data(text, url, all_slugs)
        except:
            llm_data = {"title": "Новость", "summary": "Добавлено админом", "topics": []}
        db.add(NewsSubmission(url=url, status="pending", reviewed_by=admin.id, llm_data=llm_data))
        
    elif file and file.filename:
        file_path = f"static/uploads/{file.filename}"
        os.makedirs("static/uploads", exist_ok=True)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        # Для PDF тоже можно добавить генерацию, но пока заглушка
        db.add(NewsSubmission(pdf_path=file_path, status="pending", reviewed_by=admin.id, llm_data={"title": file.filename, "summary": "PDF загружен", "topics": []}))
        
    await db.commit()
    return RedirectResponse(url="/admin/moderation", status_code=status.HTTP_303_SEE_OTHER)