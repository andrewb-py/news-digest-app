import httpx, json
from app.config import get_settings

settings = get_settings()

async def generate_news_data(text: str, source_url: str, available_topics: list[str] = None) -> dict:
    """! 
    Генерирует заголовок, саммари и темы для новости с помощью LLM.
    
    @param text Исходный текст статьи или комментария
    @param source_url URL источника для контекста
    @param available_topics Список допустимых slug тем для фильтрации (опционально)
    @return dict Словарь {"title": str, "summary": str, "topics": List[str]}
    @exception httpx.HTTPError При ошибке запроса к OpenRouter API
    @exception json.JSONDecodeError При невалидном ответе LLM
    """
    ALLOWED_TOPICS = ["tech", "science", "business", "sport", "politics"]
    topics_str = ", ".join([f'"{t}"' for t in ALLOWED_TOPICS])
    
    prompt = f"""Выдели заголовок (до 10 слов), краткое саммари (3-4 предложения) и 1-3 релевантные темы.
ВАЖНО: выбери темы ТОЛЬКО из этого списка: [{topics_str}]. Не придумывай новые.
Ответь ТОЛЬКО валидным JSON без пояснений:
{{"title": "...", "summary": "...", "topics": ["tech", "sport"]}}
Текст: {text[:2500]}
Источник: {source_url}"""
    
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}", "Content-Type": "application/json"},
            json={"model": "stepfun/step-3.5-flash", "messages": [{"role": "user", "content": prompt}], "max_tokens": 400}
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()
        content = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        if "topics" in data:
            data["topics"] = [t for t in data["topics"] if t in ALLOWED_TOPICS]
        return data