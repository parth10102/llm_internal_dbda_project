import re
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# Hardware Specs: VRAM ~3GB (4-bit)
# Phi-3.5 excels at high-quality reasoning tasks like cleaning PII
llm_cleaner = ChatOllama(model="phi3.5:latest", temperature=0)

def clean_input_text(text: str) -> str:
    """
    Advanced cleaning using Phi-3.5 to remove PII/HTML and extract core content.
    """
    # 1. Standard Regex (Pre-process)
    text = re.sub(r'http\S+|www\S+|<.*?>', '', text)
    
    # 2. Advanced LLM Cleaning
    # LLMs handle 'stickiness' and web noise better than regex alone.
    prompt = ChatPromptTemplate.from_template(
        "You are a text cleaning assistant. Clean the following text by: "
        "1. Removing all PII (names, emails, phones). "
        "2. Removing web noise like 'Share this', 'Follow us'. "
        "3. Standardizing whitespace. "
        "Only return the cleaned text.\n\nText: {text}"
    )
    
    chain = prompt | llm_cleaner
    try:
        # Truncate for efficiency; Phi-3.5 supports up to 128K context
        cleaned = chain.invoke({"text": text[:2048]}).content
        return cleaned.strip()
    except Exception as e:
        # Fallback to standard regex if LLM fails
        return re.sub(r'\s+', ' ', text).strip()