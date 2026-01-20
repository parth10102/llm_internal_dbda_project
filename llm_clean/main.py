import sys
import os
# from huggingface_hub import login
import torch
import argparse
import requests
from bs4 import BeautifulSoup
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# Import modular sequential task scripts
import cleaner            # Task 0
import lang_process        # Task 1 (Updated with GlotLID)
import domain_recog       # Task 2 (Updated with ConfliBERT)
import entity_extract     # Task 3 (Updated with IndicBERT/IndicNER)

# Standard Schema and Config imports
from schemas import AnalysisOutput
from config import SYSTEM_PROMPT

# login(token="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")

# Add safe globals for AI4Bharat/Fairseq checkpoint compatibility
if hasattr(torch.serialization, 'add_safe_globals'):
    torch.serialization.add_safe_globals([argparse.Namespace])

# Primary LLM for Synthesis (Sentiment, Summary, India Perspective)
# Hardware: VRAM ~3GB for 4-bit quantization
llm = ChatOllama(model="gemma2:2b", format="json", temperature=0, num_ctx=4096)
structured_llm = llm.with_structured_output(AnalysisOutput)

def fetch_url(url: str) -> str:
    """Robust URL fetcher to reduce token noise."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for s in soup(["script", "style", "nav", "header", "footer"]):
            s.decompose()
        return soup.get_text()
    except Exception as e:
        return f"Error: {str(e)}"

def analyze(raw_text: str):
    # --- TASK 0: Data Cleaning (Universal) ---
    cleaned_text = cleaner.clean_input_text(raw_text)
    
    # --- TASK 1: Language Detection & Transliteration (GlotLID) ---
    # GlotLID is the industry standard for 2000+ languages
    lang_info = lang_process.process_language(cleaned_text)
    
    # Use transliterated text if available, else cleaned text for further tasks
    analysis_text = lang_info['transliterated_text'] or cleaned_text
    
    # --- TASK 2: Domain Identification (ConfliBERT/BART) ---
    # Specialized for Terrorism, Military, and Radicalisation
    domains = domain_recog.analyze_domains(analysis_text)
    
    # --- TASK 3: NER (IndicBERT / IndicNER) ---
    # Beats GPT-4 on Indian entities while being 100x smaller
    entities = entity_extract.extract_entities(analysis_text)
    
    # --- TASK 4: Sentiment & Synthesis (Ollama LLM) ---
    prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT + "\nText: {text}")
    chain = prompt | structured_llm
    
    try:
        lang_info = lang_process.process_language(cleaned_text)
        domains = domain_recog.analyze_domains(cleaned_text)
        entities = entity_extract.extract_entities(cleaned_text)

        # Final reasoning pass for Summary and Sentiment
        raw_output = chain.invoke({"text": cleaned_text})
        
        # Override metadata with modular results for maximum accuracy
        raw_output.language_metadata.detected_language = lang_info['detected_language']
        raw_output.language_metadata.is_romanized = lang_info['is_romanized']
        raw_output.language_metadata.lang_code = lang_info['lang_code']
        raw_output.language_metadata.transliterated_text = lang_info['transliterated_text']
        
        raw_output.classification.domains = domains
        raw_output.entities.ner = entities

        for event in raw_output.event_mapping:
            if "-" in event.date: # Convert YYYY-MM-DD to DD/MM/YYYY
                parts = event.date.split("-")
                event.date = f"{parts[2]}/{parts[1]}/{parts[0]}"
        
        # India Perspective Guardrail
        if raw_output.sentiment == "Anti-National":
            raw_output.india_perspective = "Anti-National"
            
        return raw_output.model_dump()
        
    except Exception as e:
        return {"error": f"Pipeline failure: {str(e)}"}

if __name__ == "__main__":
    # Example manual test
    sample = "Desh ke dushmanon ko kabhi maaf nahi kiya jayega. Bharat ki akhandta sabse upar hai."
    print(analyze(sample))