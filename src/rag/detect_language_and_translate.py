import logging
logger = logging.getLogger(__name__)
logger.propagate = True
import re
import json
from call_llm import call_llm

def detect_language_and_translate(text: str) -> tuple[str, str]:
    prompt = f"""
Detect the language of the following text.
Return the result in JSON with the following keys:
- language_name: the language name in English (e.g., "Japanese", "English", "Chinese")
- translated_text: if the text is not English, translate it to English; if it is already English, return it unchanged.

Text:
{text}
"""
    raw_text = call_llm(prompt)

    cleaned = re.sub(r"^```json|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    
    # JSON parsing
    result = json.loads(cleaned)

    return result["language_name"], result["translated_text"]