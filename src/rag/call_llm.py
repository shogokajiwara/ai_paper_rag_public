import logging
logger = logging.getLogger(__name__)
logger.propagate = True
import os
import google.genai as genai
import time

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    msg = "GEMINI_API_KEY environment variable is required"
    raise ValueError(msg)
client: genai.Client = genai.Client(api_key=GEMINI_API_KEY)
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
if LLM_MODEL_NAME is None:
    raise EnvironmentError("'LLM_MODEL_NAME' is not defined.")

def call_llm(system_prompt: str) -> str:

    max_retries = 3
    retry_delay = 1
    full_messages = [{"role": "user", "parts": [{"text": system_prompt}]}]

    for _ in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=LLM_MODEL_NAME,
                contents=full_messages,
            )


            if response.text and response.text.strip():
                return str(response.text.strip())

        except Exception as e:
            logger.critical(f"[WARN] LLM API call failed: {e}")
            time.sleep(retry_delay)

    return "[ERROR] LLM returned no usable output after retries."