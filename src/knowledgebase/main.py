import yaml
import logging.config

with open("/config/logging.yml", "r") as f:
    config = yaml.safe_load(f)
logging.config.dictConfig(config)

logger = logging.getLogger(__name__)
from typing import Any, Optional
from fastapi import FastAPI
from fastapi import FastAPI
from contextlib import asynccontextmanager
from langchain_huggingface import HuggingFaceEmbeddings
from update_knowledgebase import update_knowledgebase
import requests
import os

# ==== Model Settings ====
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
if EMBEDDING_MODEL_NAME is None:
    raise EnvironmentError("'EMBEDDING_MODEL_NAME' is not defined.")

embedding_model: Optional[HuggingFaceEmbeddings] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global embedding_model
    embedding_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME
    )
    logger.critical("Embedding model preloaded at startup")

    yield  # ← ここでアプリが動作する

    # shutdown 時に必要ならここでクリーンアップ
    logger.critical("Shutting down...")


app = FastAPI(lifespan=lifespan)


@app.post("/update")
def update() -> dict[str, Any]:
    global embedding_model
    result = update_knowledgebase(["cs.AI", "cs.LG", "stat.ML", "cs.CL", "cs.CV", "cs.NE"],
        cache_dir="/cache",
        embedding_model=embedding_model
    )

    if result == 0:
        try:
            r = requests.post("http://rag:8000/trigger")
            logger.critical(f"Triggered rag: status={r.status_code}")
        except Exception as e:
            logger.critical(f"Failed to trigger rag: {e}")

    return {"result": result}

