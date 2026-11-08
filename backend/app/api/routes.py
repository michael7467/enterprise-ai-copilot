import json
import logging
import threading
import time
import urllib.request
from datetime import datetime, timezone

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.generation.llm import LLMError, is_abstention
from app.handlers import HANDLERS
from app.router.rules import route_message
from app.schemas import ChatRequest, ChatResponse, UploadedFile
from app.ingestion import uploads_index
from app.ingestion.pdf import chunk_pages, extract_pages
from app.storage.files import FileTooLarge, UnsupportedFileType, get_upload, save_meta, save_upload

router = APIRouter()
logger = logging.getLogger("janoai.api")
_log_lock = threading.Lock()


def log_request(record: dict) -> None:
    """Observability: append one JSON line per question to logs/requests.jsonl."""
    try:
        settings.request_log.parent.mkdir(parents=True, exist_ok=True)
        with _log_lock, open(settings.request_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as e:  # a logging problem must never break an answer
        logger.warning("Could not write the request log: %s", e)


@router.get("/health")
def health() -> dict:
    """Reports whether Elasticsearch and Ollama are reachable."""
    def reachable(url: str) -> bool:
        try:
            with urllib.request.urlopen(url, timeout=3):
                return True
        except Exception:
            return False
    return {
        "status": "ok",
        "elasticsearch": reachable(settings.es_url),
        "ollama": reachable(f"{settings.ollama_url}/api/tags"),
        "llm_model": settings.llm_model,
        "retrieval": "hybrid" if settings.semantic_enabled else "bm25 (light mode)",
        "rerank_enabled": settings.rerank_enabled,
    }



@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    start = time.perf_counter()
    upload = None
    if req.file_id:
        upload = get_upload(req.file_id)
        if upload is None:
            raise HTTPException(404, "Uploaded file not found.")
    decision = route_message(req.message, upload.kind if upload else None)
    record = {
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "route": decision.route,
        "model": settings.llm_model,
        "retrieval": "hybrid" if settings.semantic_enabled else "bm25",
        "rerank": settings.rerank_enabled,
        "role": req.user_role,
        "file": upload.filename if upload else None,
        "question": req.message,
    }

    def elapsed_ms() -> int:
        return round((time.perf_counter() - start) * 1000)

    try:
        response = HANDLERS[decision.route](req, decision, upload)
    except LLMError as e:
        logger.error("LLM failure: %s", e)
        log_request({**record, "status": "llm_error", "error": str(e)[:200], "latency_ms": elapsed_ms()})
        raise HTTPException(503, f"The language model is not available: {e}")
    except Exception as e:
        if type(e).__module__.startswith(("elasticsearch", "elastic_transport")):
            logger.error("Search failure: %s", e)
            log_request({**record, "status": "search_error", "error": str(e)[:200], "latency_ms": elapsed_ms()})
            raise HTTPException(503, "The document search is not available. Is Elasticsearch running?")
        raise
    response.latency_ms = elapsed_ms()
    log_request({
        **record,
        "status": "ok",
        "latency_ms": response.latency_ms,
        "confidence": response.confidence,
        "retrieval_score": response.retrieval_score,
        "sources": [c.source for c in response.citations],
        "cited": [c.index for c in response.citations if c.cited],
        "abstained": is_abstention(response.answer),
        "answer_chars": len(response.answer),
    })
    logger.info("route=%s role=%s file=%s confidence=%s cited=%s latency_ms=%d",
                decision.route, req.user_role, bool(upload), response.confidence,
                [c.index for c in response.citations if c.cited], response.latency_ms)
    return response


@router.post("/upload", response_model=UploadedFile)
async def upload(file: UploadFile = File(...)) -> UploadedFile:
    data = await file.read()
    try:
        meta, path = save_upload(file.filename or "upload", data)
    except UnsupportedFileType as e:
        raise HTTPException(415, str(e))
    except FileTooLarge as e:
        raise HTTPException(413, str(e))
    if meta.kind != "document":
        return meta  # images are stored; reading them is a later feature

   
    start = time.perf_counter()
    try:
        pages = extract_pages(path)
    except Exception as e:  # damaged or encrypted PDF
        logger.warning("Could not read %s: %s", meta.filename, e)
        raise HTTPException(422, f"Could not read this file: {e}")
    chunks = chunk_pages(pages, meta.file_id, meta.filename)
    meta.pages = len(pages)
    meta.chunks = len(chunks)
    meta.status = "ready" if chunks else "no_text"
    if chunks:
        try:
            uploads_index.index_chunks(meta.file_id, meta.filename, chunks)
        except Exception as e:
            logger.error("Indexing failed: %s", e)
            raise HTTPException(503, "The document search is not available. Is Elasticsearch running?")
    save_meta(meta)
    logger.info("upload file=%s pages=%d chunks=%d status=%s ms=%d", meta.filename, meta.pages, meta.chunks,
                meta.status, (time.perf_counter() - start) * 1000)
    return meta


