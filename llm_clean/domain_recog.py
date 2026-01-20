from transformers import pipeline

# Global cache to prevent re-loading on every call
_CLASSIFIER = None

def get_classifier():
    global _CLASSIFIER
    if _CLASSIFIER is None:
        # facebook/bart-large-mnli is the best zero-shot engine for domain detection.
        # ConfliBERT variants (eventdata-utd/ConfliBERT-scr-uncased) are best for binary/multi-label conflict detection.
        model_name = "facebook/bart-large-mnli" 
        print(f">>> Initializing Domain Identification ({model_name})...")
        _CLASSIFIER = pipeline("zero-shot-classification", model=model_name)
    return _CLASSIFIER

def analyze_domains(text, candidate_labels=None):
    """
    Task 2: Detect up to 3 domains and rank by relevance.
    Uses zero-shot classification to map text to intelligence domains.
    """
    if not candidate_labels:
        candidate_labels = [
            "Politics", "Crime", "Military", "Terrorism", 
            "Radicalisation", "Extremism in J&K", "Law and Order", 
            "Narcotics", "Left Wing Extremism"
        ]
    
    classifier = get_classifier()
    
    # Perform multi-label classification to allow overlapping domains
    result = classifier(text, candidate_labels, multi_label=True)
    
    # Filter for labels with a confidence score > 0.4 and return top 3
    # Requirements: Rank 1-3 by relevance
    top_labels = [
        label for label, score in zip(result['labels'], result['scores']) 
        if score > 0.4
    ]
    
    return top_labels[:3] if top_labels else ["General"]