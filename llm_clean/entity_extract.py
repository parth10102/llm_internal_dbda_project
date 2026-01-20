import torch
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification

# Global cache to prevent re-loading on every call
_NER_PIPELINE = None

def get_ner_pipeline():
    """Lazy loads the IndicNER model (built on IndicBERT)."""
    global _NER_PIPELINE
    if _NER_PIPELINE is None:
        # Use ai4bharat/IndicNER, the specialized model for Indian context
        model_name = "Babelscape/wikineural-multilingual-ner"
        print(f">>> Initializing NER Model ({model_name})...")
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForTokenClassification.from_pretrained(model_name)
        
        # Initialize pipeline with aggregation to group entity chunks (e.g., 'Narendra' + 'Modi')
        
        _NER_PIPELINE = pipeline(
            "ner", 
            model=model, 
            tokenizer=tokenizer, 
            aggregation_strategy="simple",
            use_fast=True
        )
    return _NER_PIPELINE

def extract_entities(text: str) -> dict:
    ner_pipe = get_ner_pipeline()
    raw_results = ner_pipe(text)
    
    refined = {"PERSON": [], "LOCATION": [], "ORGANIZATION": [], "EVENT": [], "PRODUCT": []}
    label_map = {"PER": "PERSON", "LOC": "LOCATION", "ORG": "ORGANIZATION", "EVT": "EVENT", "PROD": "PRODUCT"}
    
    for entity in raw_results:
        mapped_label = label_map.get(entity['entity_group'])
        if mapped_label:
            word = entity['word'].strip()
            word = word.replace("##", "")
            # FIX: Only accept words longer than 2 chars and ignore sub-word fragments (##)
            if word not in refined[mapped_label] and len(word) > 2 and not word.startswith("##"):
                refined[mapped_label].append(word)
    return refined

def refine_entities(ner_dict: dict) -> dict:
    """
    Legacy support for your main.py if you still want to 
    post-process LLM dictionary outputs.
    """
    categories = ["PERSON", "LOCATION", "ORGANIZATION", "EVENT", "PRODUCT"]
    refined = {cat: [] for cat in categories}
    for category, values in ner_dict.items():
        cat_upper = category.upper()
        if cat_upper in refined:
            unique_vals = list(set(values)) 
            refined[cat_upper] = [v.strip() for v in unique_vals if 0 < len(v.split()) < 5]
    return refined