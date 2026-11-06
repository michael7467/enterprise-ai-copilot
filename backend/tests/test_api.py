"""API tests with Elasticsearch and Ollama replaced by fakes. Run from backend/:  pytest -q"""
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.generation import llm
from app.main import app
from app.retrieval import search
from app.retrieval.search import Chunk, RetrievalResult
from app.router.rules import route_message

client = TestClient(app)


def chunk(i: int, doc: str) -> Chunk:
    return Chunk(chunk_id=f"{doc}::{i:03d}", doc_id=doc, title=f"Title {doc}", section=f"Section {i}",
                 text=f"Document: Title {doc} | Section: Section {i}\n\nBody {i}", body=f"Body {i}")


@pytest.fixture
def fakes(monkeypatch, tmp_path):
    """Fake retrieval and LLM; records what the LLM was asked."""
    calls = {"llm": []}
    state = {"result": RetrievalResult(chunks=[chunk(0, "dA"), chunk(1, "dB")]), "answer": "It is 90 days [1]."}

    monkeypatch.setattr(search.retriever, "search", lambda q: state["result"])

    def fake_chat(system, user, history=None):
        calls["llm"].append({"system": system, "user": user, "history": history})
        return state["answer"]
    monkeypatch.setattr(llm, "chat", fake_chat)
    monkeypatch.setattr(settings, "upload_dir", tmp_path)
    monkeypatch.setattr(settings, "rerank_enabled", False)
    install_fake_uploads_index(monkeypatch, calls)
    return state, calls


def install_fake_uploads_index(monkeypatch, calls):
    """In-memory replacement for the Elasticsearch uploads index (keyword overlap instead of BM25)."""
    from dataclasses import asdict
    from app.ingestion import uploads_index
    store = {}
    calls["indexed"] = store

    def index_chunks(file_id, filename, chunks):
        store[file_id] = [{**asdict(c), "file_id": file_id, "filename": filename} for c in chunks]

    def search(file_id, question, k):
        words = {w.lower().strip("?.,") for w in question.split() if len(w) > 3}
        scored = [(sum(w in c["text"].lower() for w in words), c) for c in store.get(file_id, [])]
        return [c for s, c in sorted(scored, key=lambda x: -x[0]) if s > 0][:k]

    def first_chunks(file_id, k):
        return sorted(store.get(file_id, []), key=lambda c: c["position"])[:k]

    monkeypatch.setattr(uploads_index, "index_chunks", index_chunks)
    monkeypatch.setattr(uploads_index, "search", search)
    monkeypatch.setattr(uploads_index, "first_chunks", first_chunks)


# ---------- router ----------
def test_router_rules():
    assert route_message("Explain deep learning", None).route == "direct"
    assert route_message("What is our leave policy?", None).route == "knowledge_base"
    assert route_message("Summarize this", "document").route == "uploaded_file"
    assert route_message("What is this?", "image").route == "vision"


def test_rrf_prefers_chunks_ranked_by_both():
    assert search.rrf(["a", "b", "c"], ["d", "b", "e"])[0] == "b"


# ---------- /chat ----------
def test_knowledge_base_answer_with_citations(fakes):
    state, calls = fakes
    r = client.post("/chat", json={"message": "What is our key rotation period?"}).json()
    assert r["route"] == "knowledge_base"
    assert r["answer"] == "It is 90 days [1]."
    assert [c["index"] for c in r["citations"]] == [1, 2]
    assert [c["cited"] for c in r["citations"]] == [True, False]
    assert r["confidence"] is None                      # gate off without reranker
    assert "[1] Document: Title dA" in calls["llm"][0]["user"]
    assert "similar topic is not enough" in calls["llm"][0]["system"]  # prompt v2


def test_gate_abstains_without_calling_llm(fakes, monkeypatch):
    state, calls = fakes
    monkeypatch.setattr(settings, "rerank_enabled", True)
    state["result"] = RetrievalResult(chunks=[chunk(0, "dA")], top_score=0.3)
    r = client.post("/chat", json={"message": "What is our canary threshold?"}).json()
    assert r["confidence"] == "abstained"
    assert r["answer"] == llm.NOT_FOUND
    assert calls["llm"] == []                            # the slow model was never called


def test_gate_low_and_high_confidence(fakes, monkeypatch):
    state, _ = fakes
    monkeypatch.setattr(settings, "rerank_enabled", True)
    state["result"] = RetrievalResult(chunks=[chunk(0, "dA")], top_score=0.7)
    assert client.post("/chat", json={"message": "our policy?"}).json()["confidence"] == "low"
    state["result"] = RetrievalResult(chunks=[chunk(0, "dA")], top_score=0.95)
    assert client.post("/chat", json={"message": "our policy?"}).json()["confidence"] == "high"


def test_model_abstention_is_reported(fakes):
    state, _ = fakes
    state["answer"] = llm.NOT_FOUND
    r = client.post("/chat", json={"message": "our policy?"}).json()
    assert r["confidence"] == "abstained"
    assert not any(c["cited"] for c in r["citations"])


def test_invalid_citation_numbers_are_ignored(fakes):
    state, _ = fakes
    state["answer"] = "Something [7] and [2]."
    r = client.post("/chat", json={"message": "our policy?"}).json()
    assert [c["cited"] for c in r["citations"]] == [False, True]


def test_direct_route_passes_history(fakes):
    _, calls = fakes
    history = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
    r = client.post("/chat", json={"message": "Explain deep learning", "history": history}).json()
    assert r["route"] == "direct" and r["citations"] == []
    assert calls["llm"][0]["history"] == history


def test_llm_down_gives_503(fakes, monkeypatch):
    def down(*a, **k):
        raise llm.LLMError("Cannot reach Ollama")
    monkeypatch.setattr(llm, "chat", down)
    r = client.post("/chat", json={"message": "Explain deep learning"})
    assert r.status_code == 503 and "language model" in r.json()["detail"]


def test_empty_message_rejected():
    assert client.post("/chat", json={"message": ""}).status_code == 422


# ---------- /upload ----------
def test_upload_then_chat_routes_to_file(fakes):
    from tests.pdfs import make_pdf
    r = client.post("/upload", files={"file": ("report.pdf", make_pdf(["Quarterly report text."]), "application/pdf")})
    assert r.status_code == 200
    up = r.json()
    assert up["kind"] == "document" and up["filename"] == "report.pdf"
    r = client.post("/chat", json={"message": "Summarize this", "file_id": up["file_id"]}).json()
    assert r["route"] == "uploaded_file"


def test_upload_image_routes_to_vision(fakes):
    up = client.post("/upload", files={"file": ("chart.png", b"\x89PNG", "image/png")}).json()
    assert client.post("/chat", json={"message": "What is this?", "file_id": up["file_id"]}).json()["route"] == "vision"


def test_upload_rejects_unsupported_type(fakes):
    assert client.post("/upload", files={"file": ("run.exe", b"MZ", "application/octet-stream")}).status_code == 415


def test_upload_rejects_too_large(fakes, monkeypatch):
    monkeypatch.setattr(settings, "max_upload_mb", 0)
    assert client.post("/upload", files={"file": ("a.txt", b"x" * 10, "text/plain")}).status_code == 413


def test_upload_path_tricks_are_neutralised(fakes):
    up = client.post("/upload", files={"file": ("../../evil.txt", b"hi", "text/plain")}).json()
    assert up["filename"] == "evil.txt"


def test_unknown_or_malicious_file_id(fakes):
    assert client.post("/chat", json={"message": "x", "file_id": "doesnotexist"}).status_code == 404
    assert client.post("/chat", json={"message": "x", "file_id": "../../etc"}).status_code == 404


def test_health_reports_services():
    r = client.get("/health").json()
    assert r["status"] == "ok"
    assert isinstance(r["elasticsearch"], bool) and isinstance(r["ollama"], bool)  # true or false, never an error
