import json
from ollama import chat
from pydantic import ValidationError
from schemas import CleanResult
from config import MODEL_NAME, SYSTEM_PROMPT

def clean_with_llm(raw_text: str) -> CleanResult:
    response = chat(
        model=MODEL_NAME,
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': raw_text},
        ],
        format=CleanResult.model_json_schema(),
        stream=False,
    )

    content = response['message']['content']

    try:
        result = CleanResult.model_validate_json(content)
    except ValidationError as e:
        raise RuntimeError(f"Bad LLM JSON output: {e}\nRaw content:\n{content}") from e

    return CleanResult.model_validate_json(content)