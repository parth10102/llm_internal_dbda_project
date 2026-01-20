import fasttext
import re
from huggingface_hub import hf_hub_download
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# Cache variables for lazy loading
_GLOTLID_MODEL = None
_XLIT_ENGINE = None

def get_glotlid():
    """Lazy loads GlotLID model."""
    global _GLOTLID_MODEL
    if _GLOTLID_MODEL is None:
        # Download and load the FastText model
        model_path = hf_hub_download(repo_id="cis-lmu/glotlid", filename="model.bin")
        _GLOTLID_MODEL = fasttext.load_model(model_path)
    return _GLOTLID_MODEL

def get_xlit_engine():
    """Lazy loads the Transliteration engine."""
    global _XLIT_ENGINE
    if _XLIT_ENGINE is None:
        from ai4bharat.transliteration import XlitEngine
        _XLIT_ENGINE = XlitEngine(beam_width=4, rescore=True)
    return _XLIT_ENGINE

def process_language(text):
    model = get_glotlid()
    predictions = model.predict(text.replace('\n', ' '), k=1)
    label = predictions[0][0].replace("__label__", "")
    
    # Split label (e.g., 'mar_Latn' or 'mar_Deva')
    parts = label.split("_")
    lang_iso = parts[0]
    # FastText might miss the Latn tag if native script is present
    detected_script = parts[1] if len(parts) > 1 else ""

    # IMPROVED CHECK: If the label is Marathi but text contains Latin letters (a-z)
    has_latin = bool(re.search(r'[a-zA-Z]{4,}', text)) # Check for words longer than 3 chars
    
    is_romanized = (detected_script == "Latn") or (lang_iso != "eng" and has_latin)
    
    trans_text = None
    if is_romanized:
        # Task 1: Label as Roman_<Lang>
        detected_language = f"Roman_{lang_iso}"
        # Trigger transliteration
        trans_text = transliterate(text, sanscript.ITRANS, sanscript.DEVANAGARI)
    else:
        detected_language = lang_iso

    return {
        "detected_language": detected_language,
        "is_romanized": is_romanized,
        "lang_code": lang_iso,
        "transliterated_text": trans_text
    }