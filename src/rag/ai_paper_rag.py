import logging
logger = logging.getLogger(__name__)
logger.propagate = True

from typing import Any
from fastapi import Request
from detect_language_and_translate import detect_language_and_translate
from build_system_prompt import build_system_prompt
from call_llm import call_llm
from extract_keywords import extract_keywords
from HybridSearch import HybridSearch
from format_observation import format_observation
from translate_to_target_language import translate_to_target_language


hybrid: HybridSearch

def ai_paper_rag(request: Request, user_question: str) -> dict[str, Any]:
    logger.info(f"user_question={user_question}")
    language_name, user_question_english = detect_language_and_translate(user_question)
    logger.info(f"language_name={language_name}")
    system_prompt_keyword = build_system_prompt(True, False, "", user_question_english)
    logger.info(f"system_prompt_keyword={system_prompt_keyword}")
    llm_output_keyword = call_llm(system_prompt_keyword)
    logger.info(f"llm_output_keyword = {llm_output_keyword}")
    list_keyword = extract_keywords(llm_output_keyword)
    logger.critical(f"list_keyword = {list_keyword}")
    system_prompt_vector = build_system_prompt(False, False, "", user_question_english)
    logger.info(f"system_prompt_vector = {system_prompt_vector}")
    llm_output_vector = call_llm(system_prompt_vector)
    logger.critical(f"llm_output_vector = {llm_output_vector}")
    hybrid = request.app.state.hybrid
    hybrid_results = hybrid.search(llm_output_vector,list_keyword)
    logger.critical(f"hybrid_results = {hybrid_results}")
    obs_text, relevant_papers = format_observation(hybrid_results,user_question)
    logger.critical(f"obs_text = {obs_text}")
    system_prompt = build_system_prompt(True,True,obs_text, user_question_english)
    logger.info(f"system_prompt = {system_prompt}")
    english_answer = call_llm(system_prompt)
    logger.info(f"english_answer = {english_answer}")

    answer = translate_to_target_language(language_name, english_answer)
    logger.info(f"answer = {answer}")

    # Format for UI
    papers = []
    for r in relevant_papers:
        logger.info(f"title = {r['title']}")
        papers.append({
            "title": r["title"],
            "url": r["url"]
        })

    return {
        "answer": answer,
        "papers": papers
    }