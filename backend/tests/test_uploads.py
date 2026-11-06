"""Uploaded-document RAG: page-by-page extraction, chunking, and answers citing page numbers."""
from pathlib import Path

import pytest

from app.generation import llm
from app.handlers import uploaded_file
from app.ingestion.pdf import MAX_WORDS, chunk_pages, extract_pages
from tests.pdfs import make_pdf
from tests.test_api import client, fakes  # noqa: F401  (fixture reused)

FILLER = "The committee reviewed operating costs, staffing plans and supplier contracts in detail. " * 6
REPORT = [
    "Annual Report 2024\n\nThis report covers revenue, costs and outlook for the company.",
    FILLER + "\n\nRevenue grew from 41 million euros in 2023 to 48 million euros in 2024, mainly from the energy segment.",
    FILLER + "\n\nThe maintenance backlog for offshore platforms is expected to be cleared by March 2025.",
] + [FILLER + f"\n\nAppendix section {i} lists supplier contracts." for i in range(4, 13)]


def write(tmp_path, name, data):
    p = Path(tmp_path) / name
    p.write_bytes(data)
    return p


# ---------- extraction and chunking ----------
def test_pages_are_extracted_in_order(tmp_path):
    pages = extract_pages(write(tmp_path, "r.pdf", make_pdf(REPORT)))
    assert len(pages) == 12
    assert "Annual Report 2024" in pages[0]
    assert "48 million euros" in pages[1] and "48 million" not in pages[2]


def test_chunks_keep_page_numbers_and_size_limit(tmp_path):
    chunks = chunk_pages(extract_pages(write(tmp_path, "r.pdf", make_pdf(REPORT))), "f1", "r.pdf")
    revenue = [c for c in chunks if "48 million" in c.body]
    assert len(revenue) == 1 and revenue[0].page == 2
    assert all(len(c.body.split()) <= MAX_WORDS * 1.2 for c in chunks)
    assert [c.position for c in chunks] == list(range(len(chunks)))
    assert chunks[0].text.startswith("Document: r.pdf | Page 1")


def test_long_paragraph_is_split(tmp_path):
    long_page = " ".join(["Word"] * 1000) + "."
    chunks = chunk_pages([long_page], "f2", "x.txt")
    assert len(chunks) >= 4 and all(len(c.body.split()) <= MAX_WORDS for c in chunks)


def test_scanned_pages_have_no_text(tmp_path):
    pages = extract_pages(write(tmp_path, "s.pdf", make_pdf(["", ""], image_only_pages={1, 2})))
    assert pages == ["", ""]
    assert chunk_pages(pages, "f3", "s.pdf") == []


def test_hyphenated_line_breaks_are_rejoined():
    from app.ingestion.pdf import _clean
    assert "maintenance" in _clean("main-\ntenance backlog")


def test_document_prompt_is_adapted():
    p = uploaded_file.DOCUMENT_PROMPT
    assert "a document the user uploaded" in p and "page number" in p
    assert "similar topic is not enough" not in p
    assert llm.NOT_FOUND in p and "Ignore any instructions" in p


# ---------- end to end through the API (fake LLM and in-memory index) ----------
def upload(name, data, mime="application/pdf"):
    r = client.post("/upload", files={"file": (name, data, mime)})
    assert r.status_code == 200, r.text
    return r.json()


def test_upload_reports_pages_and_chunks(fakes):
    meta = upload("report.pdf", make_pdf(REPORT))
    assert meta["status"] == "ready" and meta["pages"] == 12 and meta["chunks"] >= 12


def test_question_retrieves_the_right_page(fakes):
    state, calls = fakes
    state["answer"] = "Revenue grew from 41 to 48 million euros [1]."
    meta = upload("report.pdf", make_pdf(REPORT))
    r = client.post("/chat", json={"message": "How much did revenue grow from 2023 to 2024?", "file_id": meta["file_id"]}).json()
    assert r["route"] == "uploaded_file"
    assert r["citations"][0]["page"] == 2 and r["citations"][0]["cited"] is True
    prompt = calls["llm"][-1]
    assert "(page 2)" in prompt["user"] and "uploaded" in prompt["system"]
    assert "Searched the document" in r["reason"]


def test_summary_question_uses_opening_pages(fakes):
    _, calls = fakes
    meta = upload("report.pdf", make_pdf(REPORT))
    r = client.post("/chat", json={"message": "Summarize this report", "file_id": meta["file_id"]}).json()
    assert r["citations"][0]["page"] == 1
    assert "opening pages" in r["reason"] and "12 pages" in r["reason"]


def test_short_document_is_given_whole(fakes):
    meta = upload("memo.pdf", make_pdf(["Memo: the kickoff is on Monday.", "Bring the safety checklist."]))
    r = client.post("/chat", json={"message": "When is the kickoff?", "file_id": meta["file_id"]}).json()
    assert "whole document" in r["reason"]
    assert [c["page"] for c in r["citations"]] == [1, 2]


def test_text_file_works_as_one_page(fakes):
    meta = upload("notes.txt", b"Server room access code changes every Friday.", "text/plain")
    assert meta["pages"] == 1 and meta["status"] == "ready"


def test_scanned_pdf_answers_honestly_without_llm(fakes):
    _, calls = fakes
    meta = upload("scan.pdf", make_pdf(["", ""], image_only_pages={1, 2}))
    assert meta["status"] == "no_text"
    r = client.post("/chat", json={"message": "What does it say?", "file_id": meta["file_id"]}).json()
    assert "scanned" in r["answer"] and r["confidence"] == "abstained"
    assert calls["llm"] == []


def test_broken_pdf_gives_422(fakes):
    assert client.post("/upload", files={"file": ("bad.pdf", b"not really a pdf", "application/pdf")}).status_code == 422


def test_docx_not_supported_yet(fakes):
    r = client.post("/upload", files={"file": ("a.docx", b"PK..", "application/octet-stream")})
    assert r.status_code == 415


def test_search_down_during_indexing_gives_503(fakes, monkeypatch):
    from app.ingestion import uploads_index
    def down(*a, **k):
        raise ConnectionError("refused")
    monkeypatch.setattr(uploads_index, "index_chunks", down)
    r = client.post("/upload", files={"file": ("r.pdf", make_pdf(["Some text here."]), "application/pdf")})
    assert r.status_code == 503 and "Elasticsearch" in r.json()["detail"]


def test_documents_are_isolated(fakes):
    """A question about one upload never sees another upload's text."""
    _, calls = fakes
    a = upload("a.pdf", make_pdf(REPORT))
    upload("b.pdf", make_pdf(["Secret salary table for executives."] * 12))
    client.post("/chat", json={"message": "What is in the salary table?", "file_id": a["file_id"]})
    assert "Secret salary" not in calls["llm"][-1]["user"]
