from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from app.routers import auth, users, submissions, admin, news
from app.utils.dependencies import get_current_user

app = FastAPI(title="News Digest")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(submissions.router)
app.include_router(admin.router)
app.include_router(news.router)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_redirect():
    """
    Перенаправляет со старого пути /dashboard на актуальный /news/feed.

    :return: RedirectResponse на /news/feed
    """
    return RedirectResponse(url="/news/feed", status_code=302)