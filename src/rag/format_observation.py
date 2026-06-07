import logging
logger = logging.getLogger(__name__)
logger.propagate = True
from typing import Any
from split_content import split_content
from compress_with_query import compress_with_query

def format_observation(hybrid_docs: list[dict[str, Any]], user_question: str) -> tuple[str, list[dict[str, str]]]:
    lines = []
    relevant_docs = []

    for _, d in enumerate(hybrid_docs, 1):
        content = d["content"]
        logger.critical(f"content = {content}")
        meta = d["metadata"]
        logger.critical(f"meta = {meta}")

        title, abstruct = split_content(content)
        logger.critical(f"abstruct = {abstruct}")
        compressed = compress_with_query(abstruct, user_question)
        logger.critical(f"compressed = {compressed}")

        if compressed["relevance"] == 1:
            lines.append(f"- {title}\n{compressed['summary']}")

            relevant_docs.append({
                "title": title,
                "url": f"https://arxiv.org/abs/{meta.get('id')}"
            })

    return "\n".join(lines), relevant_docs