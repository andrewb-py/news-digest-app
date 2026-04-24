import httpx, re
from urllib.parse import urlparse

async def is_url_accessible(url: str) -> bool:
    """! 
    Проверяет, доступен ли URL (возвращает статус < 400).
    
    @param url Проверяемый URL
    @return True, если URL доступен, иначе False
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.head(url, follow_redirects=True)
            return r.status_code < 400
    except:
        return False

def is_valid_pdf_url(url: str) -> bool:
    """! 
    Проверяет, заканчивается ли URL на .pdf (эвристика).
    
    @param url URL для проверки
    @return True, если URL выглядит как PDF
    """
    return urlparse(url).path.lower().endswith(".pdf")