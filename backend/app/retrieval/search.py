"""Hybrid retrieval over Elasticsearch, the same setup as eval/retrieval/eval_drive_retrieval.py:
BM25 + BGE-M3 kNN, fused with reciprocal rank fusion, optionally reranked with a cross-encoder."""
import logging
from dataclasses import dataclass, field
from functools import cached_property

from app.config import settings

logger = logging.getLogger("janoai.retrieval")


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    section: str
    text: str       # header + body: what the LLM reads
    body: str
    rerank_score: float | None = None


@dataclass
class RetrievalResult:
    chunks: list[Chunk]                 # best first, at most settings.top_k
    top_score: float | None = None      # best reranker score (None when reranking is off)
    timings_ms: dict = field(default_factory=dict)


class Retriever:
    """Models load on first use (BGE-M3 is about 2.3 GB), so the API starts quickly."""

    @cached_property
    def es(self):
        from elasticsearch import Elasticsearch
        return Elasticsearch(settings.es_url, request_timeout=60)

    @cached_property
    def embedder(self):
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model %s (first request only)...", settings.embed_model)
        model = SentenceTransformer(settings.embed_model, device="cpu")
        model.max_seq_length = 512
        return model

    @cached_property
    def reranker(self):
        from sentence_transformers import CrossEncoder
        logger.info("Loading reranker %s (first request only)...", settings.reranker_model)
        return CrossEncoder(settings.reranker_model, max_length=640, device="cpu")

    # --- the three steps ---
    def embed(self, question: str) -> list[float]:
        return self.embedder.encode(question, normalize_embeddings=True).tolist()

    def bm25(self, question: str) -> list[str]:
        res = self.es.search(index=settings.es_index, size=settings.top_chunks, source=False,
                             query={"match": {"text": question}})
        return [h["_id"] for h in res["hits"]["hits"]]

    def knn(self, vector: list[float]) -> list[str]:
        res = self.es.search(index=settings.es_index, size=settings.top_chunks, source=False,
                             knn={"field": "embedding", "query_vector": vector,
                                  "k": settings.top_chunks, "num_candidates": settings.num_candidates})
        return [h["_id"] for h in res["hits"]["hits"]]

    def fetch(self, chunk_ids: list[str]) -> list[Chunk]:
        if not chunk_ids:
            return []
        res = self.es.search(index=settings.es_index, size=len(chunk_ids),
                             source_includes=["doc_id", "title", "section", "text", "body"],
                             query={"ids": {"values": chunk_ids}})
        by_id = {h["_id"]: h["_source"] for h in res["hits"]["hits"]}
        return [Chunk(chunk_id=c, **by_id[c]) for c in chunk_ids if c in by_id]

    def search(self, question: str) -> RetrievalResult:
        import time
        t = {}
        if settings.semantic_enabled:
            t0 = time.perf_counter()
            vector = self.embed(question)
            t["embed"] = time.perf_counter() - t0
            t0 = time.perf_counter()
            fused = rrf(self.bm25(question), self.knn(vector))
        else:  # light mode: keyword search only (88% recall@10 vs 93% hybrid in the evaluation)
            t0 = time.perf_counter()
            fused = self.bm25(question)
        t["search"] = time.perf_counter() - t0

        depth = settings.rerank_depth if settings.rerank_enabled else settings.top_k
        chunks = self.fetch(fused[:max(depth, settings.top_k)])
        top_score = None
        if settings.rerank_enabled and chunks:
            t0 = time.perf_counter()
            head = chunks[:settings.rerank_depth]
            scores = self.reranker.predict([(question, c.text) for c in head], batch_size=8)
            for c, s in zip(head, scores):
                c.rerank_score = float(s)
            head.sort(key=lambda c: -c.rerank_score)  # stable: ties keep hybrid order
            chunks = head + chunks[settings.rerank_depth:]
            top_score = head[0].rerank_score
            t["rerank"] = time.perf_counter() - t0
        return RetrievalResult(chunks=chunks[:settings.top_k], top_score=top_score,
                               timings_ms={k: round(v * 1000) for k, v in t.items()})


def rrf(*rankings: list[str]) -> list[str]:
    """Reciprocal rank fusion over chunk ids, best first."""
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, chunk_id in enumerate(ranking, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (settings.rrf_k + rank)
    return sorted(scores, key=scores.get, reverse=True)


retriever = Retriever()
