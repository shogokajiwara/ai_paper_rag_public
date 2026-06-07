import os
import json
from typing import Any, Generator, Sequence

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Utility for batch splitting
def batch(iterable: Sequence[Any], batch_size: int) -> Generator[Sequence[Any], None, None]:
    for i in range(0, len(iterable), batch_size):
        yield iterable[i:i + batch_size]

def update_chroma(cache_dir: str, embedding_model: Any) -> None:

    persist_dir = os.path.join(cache_dir, "chroma_db")
    embedding = embedding_model

    vectorstore = Chroma(
        collection_name="papers",
        embedding_function=embedding,
        persist_directory=persist_dir,
    )

    # Addition process
    addition_path = os.path.join(cache_dir, "addition.json")
    if os.path.exists(addition_path):
        with open(addition_path, "r", encoding="utf-8") as f:
            addition_data = json.load(f)

        if isinstance(addition_data, list) and addition_data:
            docs = []
            ids = []

            for p in addition_data:
                doc_id = p.get("id")
                if not doc_id:
                    continue
                ids.append(doc_id)

                content = f"{p.get('title', '')}\n\n{p.get('abstract', '')}"
                metadata = {
                    "id": doc_id,
                    "authors": p.get("authors", []),
                    "updated": p.get("published"),
                    "categories": p.get("categories", []),
                }

                docs.append(Document(page_content=content, metadata=metadata))

            # Delete existing IDs
            for chunk in batch(ids, 500):
                vectorstore.delete(where={"id": {"$in": chunk}})


            # Add in batches to avoid Chroma limitations
            MAX_BATCH = 5000  # A safe value smaller than 5461
            for docs_batch, ids_batch in zip(
                batch(docs, MAX_BATCH),
                batch(ids, MAX_BATCH)
            ):
                vectorstore.add_documents(docs_batch, ids=ids_batch)

    # Deletion process
    deletion_path = os.path.join(cache_dir, "deletion.json")
    if os.path.exists(deletion_path):
        with open(deletion_path, "r", encoding="utf-8") as f:
            deletion_data = json.load(f)

        if isinstance(deletion_data, list) and deletion_data:
            ids_to_delete = [item.get("id") for item in deletion_data if "id" in item]
            for chunk in batch(ids_to_delete, 500):
                vectorstore.delete(where={"id": {"$in": chunk}})


if __name__ == "__main__":
    embedding_model = HuggingFaceEmbeddings(
        model_name = "BAAI/bge-base-en-v1.5",
    )
    update_chroma("/cache",embedding_model)
