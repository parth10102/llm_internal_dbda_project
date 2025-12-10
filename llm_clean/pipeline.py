from text_sources import is_url, extract_page_text
from llm_client import clean_with_llm
from schemas import CleanResult

def process_input(raw: str) -> CleanResult:
    if is_url(raw):
        text = extract_page_text(raw)
    else:
        text = raw

    return clean_with_llm(text)