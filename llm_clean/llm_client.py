import json
import re
from ollama import chat
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from pydantic import ValidationError

from schemas import CleanResult
from config import MODEL_NAME, SYSTEM_PROMPT


def fallback_build_result(raw_text: str) -> dict:
    """If LLM JSON is invalid, build a simple dict with the 4 base fields."""
    text = raw_text.strip()

    try:
        lang = detect(text) if text else "unknown"
    except LangDetectException:
        lang = "unknown"

    hashtags = re.findall(r'#[^\s.,!?]+', text)
    mentions = re.findall(r'@[^\s.,!?]+', text)

    boilerplate_phrases = [
        "मेरे चैनल को सब्सक्राइब करें",
        "मेरे चैनल को सब्सक्राइब करो",
        "Subscribe to my channel",
        "Like and share",
        "Follow for more",
    ]
    cleaned = text
    for bp in boilerplate_phrases:
        cleaned = cleaned.replace(bp, "")
    cleaned = " ".join(cleaned.split())

    return {
        "language": lang,
        "cleaned_text": cleaned,
        "hashtags": sorted(set(hashtags)),
        "mentions": sorted(set(mentions)),
    }

def infer_domain(cleaned_text: str) -> str:
    """
    Simple heuristic domain classifier.
    Prefer 'news_article' for long, article-like texts.
    """
    text = cleaned_text.strip()
    length = len(text)
    lines = text.count("\n") + 1
    lower = text.lower()

    # 1) Very short with hashtags/mentions -> tweet
    if length <= 280 and ("#" in text or "@" in text):
        return "tweet"

    # 2) Short and video-like -> video_description
    if length <= 600 and ("youtube" in lower or "video" in lower):
        return "video_description"

    # 3) Long text -> news_article
    #    Use either character length OR line count so we handle single-line blobs.
    if length >= 800 or lines >= 5:
        return "news_article"

    # 4) Fallback
    return "social_post"

def make_main_text(cleaned_text: str, hashtags, mentions) -> str:
    """Remove literal hashtags and mentions from cleaned_text."""
    text = cleaned_text
    for h in hashtags:
        text = text.replace(h, "")
    for m in mentions:
        text = text.replace(m, "")
    return " ".join(text.split())

def clean_with_llm(raw_text: str) -> CleanResult:
    response = chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": raw_text},
        ],
        format="json",
        stream=False,
        options={"num_predict": 256, "temperature": 0.1},
    )

    content = response["message"]["content"]

    # Try to parse LLM JSON; if it fails, silently use fallback dict
    try:
        base = json.loads(content)          # expected: 4 keys
    except json.JSONDecodeError:
        base = fallback_build_result(raw_text)

    # Ensure required keys exist
    language = base.get("language", "unknown")
    cleaned_text = base.get("cleaned_text", raw_text.strip())
    hashtags = base.get("hashtags", [])
    mentions = base.get("mentions", [])

    # Derive domain & main_text locally
    domain = infer_domain(cleaned_text)
    main_text = make_main_text(cleaned_text, hashtags, mentions)

    return CleanResult(
        language=language,
        domain=domain,
        main_text=main_text,
        cleaned_text=cleaned_text,
        hashtags=hashtags,
        mentions=mentions,
    )