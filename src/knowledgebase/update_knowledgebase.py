from typing import Any, Optional

from create_current_and_previous_json import create_current_and_previous_json
from create_addition_and_deletion_json import create_addition_and_deletion_json
from update_chroma import update_chroma
import logging
from langchain_huggingface import HuggingFaceEmbeddings
logger = logging.getLogger(__name__)

def update_knowledgebase(categories: list[str],cache_dir: str, embedding_model: Optional[Any]) -> int:
    """
    Executes create_current_and_previous_json.
    - If return value is 0, executes create_addition_and_deletion_json and update_chroma, then returns 0.
    - If return value is 1, returns 1.
    """

    result = create_current_and_previous_json(categories, cache_dir)
    logger.critical(f"create_current_and_previous_json result={result}")

    if result == 0:
        # Generate diff
        create_addition_and_deletion_json(cache_dir)
        # Update Chroma
        update_chroma(cache_dir, embedding_model=embedding_model)
        return 0

    return 1

if __name__ == "__main__":
    embedding_model = HuggingFaceEmbeddings(
        model_name = "BAAI/bge-base-en-v1.5",
    )
    TARGET_CATEGORIES = [
    "cs.AI",
    "cs.LG",
    "stat.ML",
    "cs.CL",
    "cs.CV",
    "cs.NE",
    ]
    final = update_knowledgebase(TARGET_CATEGORIES,"/cache",embedding_model)
    print(final)
