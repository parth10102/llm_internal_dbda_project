from pydantic import BaseModel
from typing import List

class CleanResult(BaseModel):
    language: str
    # cleaned_text: str
    main_text: str
    hashtags: List[str]
    mentions: List[str]
    other_metadata: List[str]