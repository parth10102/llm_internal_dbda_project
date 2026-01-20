from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal

class LanguageMetadata(BaseModel):
    detected_language: str = Field(description="Native language, e.g., 'Hindi' or 'Roman_Hindi'")
    is_romanized: bool = Field(description="True if the text is in English script but an Indian language")
    lang_code: str = Field(None, description="e.g., 'hi', 'mr', 'ta', 'bn'")
    transliterated_text: Optional[str] = Field(None, description="Native script version of Romanized text")

class Classification(BaseModel):
    domains: List[Literal["Politics", "Crime", "Military", "Terrorism", "Radicalisation", 
                          "Extremism in J&K", "Law and Order", "Narcotics", "Left Wing Extremism", "General"]] = Field(
        description="Rank up to 3 domains by relevance", max_items=3)

class Relevancy(BaseModel):
    relevant_to: List[str] = Field(description="Specific match topics (e.g., Narcotics, Terrorism)")
    confidence: float = Field(ge=0.0, le=1.0)
    level: Literal["High", "Medium", "Low"]

class Entities(BaseModel):
    ner: Dict[str, List[str]] = Field(default_factory=dict, description="Categorized entities: {'PERSON': [], 'LOCATION': [], 'ORGANIZATION': [], 'CRIME': []}")

class EventMapping(BaseModel):
    event_name: str
    date: str = Field(description="STRICT dd/mm/yyyy format only")
    participants: List[str] = Field(default_factory=list)

class AnalysisOutput(BaseModel):
    language_metadata: LanguageMetadata
    classification: Classification
    country_id: Literal["India", "Pakistan", "Sri Lanka", "Afghanistan", "Nepal", "Bangladesh", "China", "Abroad"]
    relevancy: Relevancy
    entities: Entities
    event_mapping: List[EventMapping]
    sentiment: str = Field(description="Positive, Negative, Neutral, or Anti-National")
    india_perspective: Optional[str] = None
    summary: str = Field(description="3-4 sentence summary (~25% of original length)")