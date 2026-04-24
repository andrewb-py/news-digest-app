import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import get_settings
from app.database import async_session
from app.models.user import User, UserSettings
from app.models.topic import UserTopic
from sqlalchemy import select

settings = get_settings()

async def _send_email(to_email: str, subject: str, html_body: str):
    """! 
    Отправляет HTML-письмо через SMTP-сервер.
    
    @param to_email Адрес получателя
    @param subject Тема письма
    @param html_body HTML-содержимое письма
    @exception aiosmtplib.SMTPException При ошибках соединения или аутентификации
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("SMTP не настроен, пропуск отправки")
        return

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = settings.SMTP_USER
    msg['To'] = to_email
    msg.attach(MIMEText(html_body, 'html'))

    try:
        async with aiosmtplib.SMTP(hostname=settings.SMTP_HOST, port=settings.SMTP_PORT, start_tls=True) as smtp:
            await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            await smtp.send_message(msg)
        print(f"Письмо отправлено: {to_email}")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

async def notify_users_about_new_news(news_id: int):
    """! 
    Рассылает уведомления пользователям о новой новости, если она относится к их интересам.
    
    @param news_id ID новой публикации
    @exception Exception При ошибках отправки (логируются, но не прерывают выполнение)
    """
    async with async_session() as db:
        from app.models.news import NewsItem
        news = (await db.execute(select(NewsItem).where(NewsItem.id == news_id))).scalar_one_or_none()
        if not news: return

        users = (await db.execute(
            select(User).join(UserSettings).where(UserSettings.email_notifications == True)
        )).scalars().all()

        for user in users:
            user_topic_ids = set((await db.execute(
                select(UserTopic.topic_id).where(UserTopic.user_id == user.id)
            )).scalars().all())
            news_topic_ids = {t.id for t in news.topics}
            
            if user_topic_ids.intersection(news_topic_ids):
                html = f"""
                <h3>📰 Новая новость по вашим темам</h3>
                <p><b>{news.title}</b></p>
                <p>{news.summary[:200]}...</p>
                <a href="{news.original_url}" target="_blank">Читать оригинал</a>
                <hr><small><a href="http://localhost:8000/news/feed">Перейти в ленту</a></small>
                """
                await _send_email(user.email, "Новый дайджест новостей", html)