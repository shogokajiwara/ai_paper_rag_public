import logging
logger = logging.getLogger(__name__)
logger.propagate = True

from typing import Any
from call_llm import call_llm
from safe_json_loads import safe_json_loads

def compress_with_query(text: str, user_question: str) -> dict[str, Any]:
    prompt = f"""
User question:
{user_question}

Analyze the Document and output ONLY a JSON object in the following format:

{{
  "relevance": 1 or 0,   // 1 if the Document contains information relevant to the User question, otherwise 0
  "summary": "Extract ONLY the information from the Document that is relevant to the User question. Then summarize it concisely in English in 20 to 30 words."
}}

Rules:
- If relevance = 0, summary must be an empty string "".
- Do NOT include any explanation outside the JSON.
- Do NOT include RELEVANT or NOT_RELEVANT in the summary.
- Escape all double quotes inside strings using \".
- Never output unescaped quotes inside the summary.
- The output MUST be valid JSON that can be parsed by json.loads().

Document:
{text}
"""
    output = call_llm(prompt)
    logger.critical(f"output = {output}")
    data = safe_json_loads(output)
    return data