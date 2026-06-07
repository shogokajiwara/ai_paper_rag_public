import logging
logger = logging.getLogger(__name__)
logger.propagate = True
from get_current_date import get_current_date

def build_system_prompt(keyword_search: bool, observed: bool, observation_text: str, user_question: str) -> str:
 
    if not observed:
        if not keyword_search:
            return f"""
You must output in English only.
You provide a vector search query for the user question about the latest AI.
Keep all specialized AI terminology and craft concise queries that preserve the full meaning.

user question :{user_question}
"""
        else:
            return f"""
You must output in English only.
You provide keyword search queries for the user question about the latest AI.
Keep only the AI-related technical keywords that represent the query. If none apply, leave it blank.

user question :{user_question}
"""
    else:
        today = get_current_date()
        if not observation_text == "":
            return f"""    
You must output in English only.
You provide answers about the latest AI technologies as of {today} by drawing on research papers.
After reading the summary of the following papers, answer the user question by referring to the summary."

user question :{user_question}

summary of papers:{observation_text}

"""
        else:
            return f"""
You must output in English only.
You provide answers about the latest AI technologies as of {today} based on your own knowledge.
Answer the user question using your own knowledge.
Begin the response with: 'Although no answer to the user question was found in the latest papers, in general'.

user question :{user_question}
"""