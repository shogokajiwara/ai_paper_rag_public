import logging
logger = logging.getLogger(__name__)
logger.propagate = True

def split_content(content: str) -> tuple[str, str]:
    title, abstract = content.split("\n\n", 1)
    return title.strip(), abstract.strip()