"""The Ollama client and the retriever against fake services (no real Ollama, Elasticsearch or models)."""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from app.config import settings
from app.generation import llm
from app.retrieval import search


@pytest.fixture
def fake_ollama(monkeypatch):
    seen = []

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            seen.append(body)
            if body["model"] == "no-think-model" and "think" in body:
                self.send_response(400); self.end_headers()
                self.wfile.write(b'{"error":"model does not support thinking"}'); return
            out = {"message": {"content": "<think>hidden</think>Answer [1]."}}
            self.send_response(200); self.end_headers(); self.wfile.write(json.dumps(out).encode())

    server = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setattr(settings, "ollama_url", f"http://127.0.0.1:{server.server_port}")
    yield seen
    server.shutdown()


def test_ollama_chat_strips_thinking_and_sends_settings(fake_ollama):
    assert llm.chat("sys", "question") == "Answer [1]."
    body = fake_ollama[0]
    assert body["think"] is False and body["options"]["temperature"] == 0
    assert body["messages"][0] == {"role": "system", "content": "sys"}


def test_ollama_retries_without_think(fake_ollama, monkeypatch):
    monkeypatch.setattr(settings, "llm_model", "no-think-model")
    assert llm.chat("sys", "q") == "Answer [1]."
    assert "think" not in fake_ollama[-1]


def test_ollama_unreachable(monkeypatch):
    monkeypatch.setattr(settings, "ollama_url", "http://127.0.0.1:9")
    with pytest.raises(llm.LLMError):
        llm.chat("sys", "q")


class FakeES:
    def __init__(self):
        self.docs = {f"c{i}": {"doc_id": f"d{i}", "title": f"T{i}", "section": "s", "text": f"text {i}", "body": f"body {i}"}
                     for i in range(20)}
    def search(self, index, size, query=None, knn=None, **kw):
        if query and "ids" in query:
            ids = query["ids"]["values"]
            return {"hits": {"hits": [{"_id": i, "_source": self.docs[i]} for i in reversed(ids)]}}  # any order
        order = [f"c{i}" for i in range(20)] if query else [f"c{i}" for i in (5, 0, 1, 2, 3, 4)]
        return {"hits": {"hits": [{"_id": i} for i in order[:size]]}}


class FakeReranker:
    def predict(self, pairs, batch_size=8):
        return [0.99 if t == "text 7" else 0.1 for _, t in pairs]  # c7 is the truly relevant chunk


def make_retriever(monkeypatch, rerank: bool):
    r = search.Retriever()
    r.__dict__["es"] = FakeES()          # fill the cached properties with fakes
    r.__dict__["reranker"] = FakeReranker()
    monkeypatch.setattr(r, "embed", lambda q: [0.0] * 4)
    monkeypatch.setattr(settings, "rerank_enabled", rerank)
    return r


def test_hybrid_without_reranker_keeps_fused_order(monkeypatch):
    res = make_retriever(monkeypatch, rerank=False).search("q")
    assert [c.chunk_id for c in res.chunks] == ["c0", "c1", "c5", "c2"]   # ranked by both lists first
    assert res.top_score is None


def test_reranker_moves_relevant_chunk_to_top(monkeypatch):
    res = make_retriever(monkeypatch, rerank=True).search("q")
    assert res.chunks[0].chunk_id == "c7" and res.top_score == 0.99
    assert len(res.chunks) == settings.top_k


def test_light_mode_uses_bm25_only_and_never_embeds(monkeypatch):
    r = make_retriever(monkeypatch, rerank=False)
    monkeypatch.setattr(settings, "semantic_enabled", False)
    def no_embed(q):
        raise AssertionError("BGE-M3 must not be used in light mode")
    monkeypatch.setattr(r, "embed", no_embed)
    res = r.search("q")
    assert [c.chunk_id for c in res.chunks] == ["c0", "c1", "c2", "c3"]  # plain BM25 order
