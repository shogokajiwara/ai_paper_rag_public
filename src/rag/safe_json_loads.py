import logging
logger = logging.getLogger(__name__)
logger.propagate = True
from typing import Any, cast
import json
import re

def safe_json_loads(text: str) -> dict[str, Any]:
    cleaned = text.replace("```json", "").replace("```", "").strip()

    try:
        return cast(dict[str, Any], json.loads(cleaned))
    except json.JSONDecodeError:
        pass

    m = re.search(r'"summary"\s*:\s*"(?P<val>.*?)"', cleaned, re.DOTALL)
    if not m:
        return {"relevance": 0, "summary": ""}

    summary_val = m.group("val")

    fixed_val = re.sub(r'(?<!\\)"', r'\"', summary_val)

    fixed_json = cleaned.replace(summary_val, fixed_val)

    try:
        return cast(dict[str, Any], json.loads(fixed_json))
    except Exception:
        return {"relevance": 0, "summary": ""}