import traceback
import yaml
import logging.config

with open("/config/logging.yml", "r") as f:
    config = yaml.safe_load(f)
logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, shutil
import asyncio
import uuid
from ai_paper_rag import ai_paper_rag
from HybridSearch import HybridSearch

tasks = {}
active_ws = set()

update_lock = asyncio.Lock()

# -----------------------------
# Lifespan（shutdown 安定化）
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.critical("[LIFESPAN] startup")

    async with update_lock:
        reload_rag()

    yield

    logger.critical("[LIFESPAN] shutdown: cancelling tasks...")
    for _, task in list(tasks.items()):
        task.cancel()
    tasks.clear()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_external_data():

    # --- chroma_db のアトミック置換 ---
    src_db = "/cache/chroma_db"
    dst_db = "/data/chroma_db"
    tmp_db = "/data/chroma_db_tmp"

    # --- JSON のアトミック置換 ---
    src_json = "/cache/all_categories.json"
    dst_json = "/data/all_categories.json"
    tmp_json = "/data/all_categories.json.tmp"

    # -----------------------------
    # chroma_db の更新
    # -----------------------------
    if not os.path.exists(src_db):
        logger.critical(f"コピー元が存在しません: {src_db}")
        return

    try:
        # tmp を作り直す
        shutil.rmtree(tmp_db, ignore_errors=True)
        shutil.copytree(src_db, tmp_db)

        # dst を削除（busy でも成功する）
        shutil.rmtree(dst_db, ignore_errors=True)

        # tmp → dst をアトミック置換
        os.rename(tmp_db, dst_db)

        logger.critical("アトミック置き換え完了: chroma_db")

    except Exception as e:
        logger.critical(f"[ERROR] chroma_db コピー失敗: {e}")

    # -----------------------------
    # all_categories.json の更新
    # -----------------------------
    try:
        if os.path.exists(src_json):

            # tmp を作成
            shutil.copy2(src_json, tmp_json)

            # dst を削除（存在しなくても OK）
            if os.path.exists(dst_json):
                os.remove(dst_json)

            # tmp → dst をアトミック置換
            os.rename(tmp_json, dst_json)

            logger.critical("アトミック置き換え完了: all_categories.json")

        else:
            logger.critical(f"JSON が存在しません: {src_json}")

    except Exception as e:
        logger.critical(f"[ERROR] JSON コピー失敗: {e}")

def reload_rag():
    logger.critical("[RAG RELOAD] start")

    # 外部データコピー
    try:
        load_external_data()
        logger.critical("[RAG RELOAD] external data copied")
    except Exception as e:
        logger.critical(f"[RAG RELOAD ERROR] external data copy failed: {e}")

    # HybridSearch 再生成
    try:
        app.state.hybrid = HybridSearch("/data/chroma_db","/data/all_categories.json")
        logger.critical("[RAG RELOAD] HybridSearch reloaded")
    except Exception as e:
        logger.critical(f"[RAG RELOAD ERROR] HybridSearch init failed: {e}")

    logger.critical("[RAG RELOAD] done")



@app.post("/trigger")
async def trigger():
    logger.critical("[TRIGGER] manual reload requested")

    async with update_lock:
        reload_rag()

    return {"status": "updated"}

# -----------------------------
# WebSocket（timeout + keepalive）
# -----------------------------
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    active_ws.add(ws)
    logger.critical(f"[WS] connected: {ws}")

    async def keepalive():
        while True:
            try:
                await ws.send_json({"type": "ping"})
                await asyncio.sleep(20)
            except:
                break

    keepalive_task = asyncio.create_task(keepalive())

    try:
        while True:
            try:
                msg = await asyncio.wait_for(ws.receive(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            if msg["type"] == "websocket.disconnect":
                break

    except Exception as e:
        logger.critical(f"[WS ERROR] {e}")

    finally:
        active_ws.discard(ws)
        keepalive_task.cancel()
        logger.critical(f"[WS] disconnected: {ws}")

# -----------------------------
# API
# -----------------------------
class RunRequest(BaseModel):
    query: str

class StartJobRequest(BaseModel):
    jobId: str
    query: str

class CancelRequest(BaseModel):
    jobId: str

@app.post("/run")
async def run(payload: RunRequest):
    if update_lock.locked():
        logger.critical("[RUN] rejected: updating in progress")
        return {"status": "updating"}

    job_id = str(uuid.uuid4())
    logger.critical(f"[RUN] new jobId = {job_id}")
    return {"jobId": job_id}


@app.post("/start-job")
async def start_job(payload: StartJobRequest, request: Request):
    job_id = payload.jobId
    query = payload.query

    if job_id in tasks:
        tasks[job_id].cancel()

    tasks[job_id] = asyncio.create_task(run_rag_and_push(request, job_id, query))
    logger.critical(f"[START] job started: {job_id}")
    return {"status": "started"}

@app.post("/cancel")
async def cancel(payload: CancelRequest):
    job_id = payload.jobId

    # ★ ジョブ停止をバックグラウンドに逃がす
    asyncio.create_task(_cancel_job(job_id))
    logger.critical(f"[CANCEL] job cancelled: {job_id}")

    # ★ HTTP は即返す（ここが重要）
    return {"status": "accepted"}

async def _cancel_job(job_id):
    if job_id in tasks:
        tasks[job_id].cancel()
        tasks.pop(job_id, None)

async def run_rag_and_push(request: Request, job_id: str, query: str):
    try:
        logger.critical(f"ai_paper_rag({query})")
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, ai_paper_rag, request, query)
        logger.critical(f"[DEBUG] result = {result}")
        logger.critical(f"({query})")

        # ★★★ ここに入れる（active_ws の数を確認） ★★★
        logger.critical(f"[WS COUNT] active_ws = {len(active_ws)}")
        for ws in list(active_ws):
            try:
                logger.critical(f"[WS SEND] to {ws}, jobId={job_id}")
                await ws.send_json({
                    "type": "result",
                    "jobId": job_id,
                    "answer": result["answer"],
                    "papers": result["papers"],
                })
                logger.critical(f"[WS SEND DONE] jobId={job_id}")

            except Exception as e:
                logger.critical(f"[WS SEND ERROR] {e}")

    except asyncio.CancelledError:
        logger.critical(f"[JOB CANCELLED] {job_id}")

    except Exception as e:
        logger.critical(f"[JOB ERROR] {e}")
        traceback.print_exc()

    finally:
        tasks.pop(job_id, None)