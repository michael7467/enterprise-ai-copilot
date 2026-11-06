"""Uploaded documents live in their own Elasticsearch index, separate from the company knowledge base.
Every search is filtered by file_id, so a question only ever sees the document uploaded with it."""
from dataclasses import asdict

from app.config import settings
from app.ingestion.pdf import PageChunk

MAPPINGS = {
    "properties": {
        "file_id": {"type": "keyword"},
        "filename": {"type": "keyword"},
        "chunk_id": {"type": "keyword"},
        "page": {"type": "integer"},
        "position": {"type": "integer"},
        "text": {"type": "text", "analyzer": "english"},
        "body": {"type": "text", "index": False},
    }
}

_es = None


def es():
    global _es
    if _es is None:
        from elasticsearch import Elasticsearch
        _es = Elasticsearch(settings.es_url, request_timeout=60)
    return _es


def ensure_index() -> None:
    if not es().indices.exists(index=settings.uploads_index):
        es().indices.create(index=settings.uploads_index, mappings=MAPPINGS,
                            settings={"number_of_shards": 1, "number_of_replicas": 0})


def index_chunks(file_id: str, filename: str, chunks: list[PageChunk]) -> None:
    from elasticsearch import helpers
    ensure_index()
    actions = ({"_index": settings.uploads_index, "_id": c.chunk_id,
                "_source": {**asdict(c), "file_id": file_id, "filename": filename}} for c in chunks)
    helpers.bulk(es(), actions, refresh="wait_for")  # searchable as soon as the upload returns


def search(file_id: str, question: str, k: int) -> list[dict]:
    """BM25 within one document."""
    res = es().search(index=settings.uploads_index, size=k,
                      query={"bool": {"must": {"match": {"text": question}},
                                      "filter": {"term": {"file_id": file_id}}}})
    return [h["_source"] for h in res["hits"]["hits"]]


def first_chunks(file_id: str, k: int) -> list[dict]:
    """The document's opening chunks, in order (used for whole-document and summary questions)."""
    res = es().search(index=settings.uploads_index, size=k, sort=[{"position": "asc"}],
                      query={"term": {"file_id": file_id}})
    return [h["_source"] for h in res["hits"]["hits"]]
