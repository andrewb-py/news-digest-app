import httpx, pdfplumber, io
from trafilatura import extract

async def fetch_web_content(url: str) -> str:
    """
    Извлекает основной текст статьи с веб-страницы с помощью trafilatura.

    :param url: URL веб-страницы
    :return: Очищенный текст статьи или первые 5000 символов HTML
    :raises httpx.HTTPError: Если URL недоступен или вернул ошибку
    """
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, follow_redirects=True)
        r.raise_for_status()
        return extract(r.text, url=url) or r.text[:5000]

def extract_pdf_text(file_path: str) -> str:
    """
    Извлекает текст из PDF-файла с использованием pdfplumber.

    :param file_path: Путь к PDF-файлу на диске
    :return: Извлечённый текст (не более 5000 символов)
    :raises FileNotFoundError: Если файл не найден
    :raises pdfplumber.PDFSyntaxError: Если файл повреждён
    """
    text = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages[:10]:
            if page.extract_text():
                text.append(page.extract_text())
    return "\n".join(text)[:5000]