import logging
logger = logging.getLogger(__name__)
logger.propagate = True

import re

def extract_keywords(query: str) -> list[str]:
    # Split by spaces and commas
    keywords = re.split(r"[,\\s]+", query)

    # Remove empty strings and convert to lowercase
    keywords = [kw.lower() for kw in keywords if kw]

    # Remove duplicates (preserve order)
    keywords = list(dict.fromkeys(keywords))

    return keywords