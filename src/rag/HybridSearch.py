import logging
logger = logging.getLogger(__name__)
logger.propagate = True
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from typing import Any
import json
import os

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
if EMBEDDING_MODEL_NAME is None:
    raise EnvironmentError("'EMBEDDING_MODEL_NAME' is not defined.")

class HybridSearch:
    embedding: HuggingFaceEmbeddings
    vectorstore: Chroma
    json_data: list[dict[str, Any]]


    def __init__(self, persist_dir: str, json_path: str) -> None:
        self.embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        self.vectorstore = Chroma(
            collection_name="papers",
            embedding_function=self.embedding,
            persist_directory=persist_dir,
        )

        with open(json_path, "r") as f:
            self.json_data = json.load(f)
       
    def vector_search(self, vector_query: str, keyword_hit_ids: list[str], top_k: int) -> list[str]:
        logger.critical("[VSEARCH] start")
        logger.critical(f"[VSEARCH] vector_query = {vector_query}")
        logger.critical(f"[VSEARCH] keyword_hit_ids = {keyword_hit_ids}")
        # --- 1. Vector search across all documents ---
        total_docs = len(self.json_data)
        logger.critical(f"[VSEARCH] total_docs = {total_docs}")

        logger.critical("[VSEARCH] calling similarity_search_with_score()")
        vector_results = self.vectorstore.similarity_search_with_score(
            vector_query.strip(),
            #k=total_docs
            k=100
        )
        logger.critical(f"[VSEARCH] similarity_search_with_score() returned {len(vector_results)} results")

        # --- 2. Top k vector search results ---
        logger.critical("[VSEARCH] extracting top_k vector results")
        vector_top_ids = [
            doc.metadata.get("id", doc.id)
            for doc, _ in vector_results[:top_k]
        ]
        logger.critical(f"[VSEARCH] vector_top_ids = {vector_top_ids}")

        # --- 3. Extract keyword search hits not in top k vector search results ---
        keyword_not_in_top = set(keyword_hit_ids) - set(vector_top_ids)
        logger.critical(f"[VSEARCH] keyword_not_in_top = {keyword_not_in_top}")
        # --- 4. Extract top k vector ranked documents from keyword hits ---
        logger.critical("[VSEARCH] scanning vector_results for keyword hits")
        keyword_vector_top_ids = []
        for doc, _ in vector_results:
            doc_id = doc.metadata.get("id", doc.id)
            if doc_id in keyword_not_in_top:
                keyword_vector_top_ids.append(doc_id)
                logger.critical(f"[VSEARCH] added keyword_vector_top_id = {doc_id}")
                if len(keyword_vector_top_ids) >= top_k:
                    break
        
        logger.critical(f"[VSEARCH] keyword_vector_top_ids = {keyword_vector_top_ids}")

        # --- 5. Merge the two lists and return ---
        merged = vector_top_ids + keyword_vector_top_ids
        logger.critical(f"[VSEARCH] merged result = {merged}")
        return merged


    def keyword_search(self, keyword_query: list[str]) -> list[str]:

        if not keyword_query:
            return []

        # --- Create a hit list for each keyword ---
        hits_by_keyword: dict[str, list[str]] = {kw: [] for kw in keyword_query}

        for item in self.json_data:
            text = f"{item.get('title', '')}\n\n{item.get('abstract', '')}"
            text_lower = text.lower()
            for kw in keyword_query:
                if kw in text_lower:
                    doc_id = item.get("id") 
                    assert doc_id is not None
                    hits_by_keyword[kw].append(doc_id)

        # --- All hits as OR search ---
        all_hits = set()
        for kw in keyword_query:
            all_hits.update(hits_by_keyword[kw])

        return list(all_hits)
    def search(self, vector_query: str, keyword_query: list[str]) -> list[dict[str, Any]]:
        logger.critical("[SEARCH] start")
        logger.critical(f"[SEARCH] vector_query = {vector_query}")
        logger.critical(f"[SEARCH] keyword_query = {keyword_query}")

        keyword_ids = self.keyword_search(keyword_query)
        logger.critical(f"[SEARCH] keyword_ids = {keyword_ids}")
        all_ids = self.vector_search(vector_query, keyword_ids, 5)
        logger.critical(f"[SEARCH] all_ids = {all_ids} (len={len(all_ids)})")

        hybrid_results = []
        logger.critical("[SEARCH] start loop over all_ids")

        for i, doc_id in enumerate(all_ids):
            logger.critical(f"[SEARCH] loop i={i}, doc_id={doc_id}")
            result = self.vectorstore.get(where={"id": doc_id})
            logger.critical(f"[SEARCH] get() done for doc_id={doc_id}, result_keys={list(result.keys())}")
            if len(result["documents"]) == 0:
                logger.critical(f"[SEARCH] empty documents for doc_id={doc_id}")
                continue

            text = result["documents"][0]
            meta = result["metadatas"][0]
            logger.critical(f"[SEARCH] append result for doc_id={doc_id}, title={meta.get('title')}")

            hybrid_results.append({
                "content": text,
                "metadata": meta
            })
        logger.critical(f"[SEARCH] done, hybrid_results len={len(hybrid_results)}")
        return hybrid_results
