from pydantic import BaseModel, Field
from typing import List, Dict, Any


class NER(BaseModel):
    PERSON: List[Dict[str, Any]] = Field(default_factory=list)
    LOCATION: List[Dict[str, Any]] = Field(default_factory=list)
    ORGANIZATION: List[Dict[str, Any]] = Field(default_factory=list)
    PRODUCT: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        extra = "allow"


class AnalysisOutput(BaseModel):
    reasoning_summary: str = ""
    original_input: str = ""
    language_scripts: List[Dict[str, Any]] = Field(default_factory=list)
    translation: str = ""
    transliteration: str = ""
    ner: NER = Field(default_factory=NER)
    events: List[Dict[str, Any]] = Field(default_factory=list)
    country_id: List[Dict[str, Any]] = Field(default_factory=list)
    domain: List[Dict[str, Any]] = Field(default_factory=list)
    summary: str = ""
    execution_time_sec: float = 0.0
    gpu_utilisation: str = ""
    memory_usage: str = ""
    
    class Config:
        extra = "allow"