from urllib.parse import urlparse
import requests
import trafilatura

def is_url(text: str) -> bool:
    parsed = urlparse(text.strip())

    return bool(parsed.scheme and parsed.netloc)

def extract_page_text(url: str) -> str:
    downloaded = trafilatura.fetch_url(url)

    if not downloaded:
        downloaded = requests.get(url, timeout=15).text

    return trafilatura.extract(downloaded, include_links=False) or ""