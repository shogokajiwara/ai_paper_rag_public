import logging
logger = logging.getLogger(__name__)
logger.propagate = True
from typing import cast
from call_llm import call_llm

def translate_to_target_language(language_name: str, english_text: str) -> str:
    # ★ Do nothing if English ★
    if language_name.lower() == "english":
        return english_text

    prompt = f"""
Translate the following English text into {language_name}.
Return only the translated text, with no explanations.

Text:
{english_text}
"""

    return cast(str, call_llm(prompt) if call_llm(prompt) else "")