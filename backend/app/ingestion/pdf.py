"""Turn an uploaded file into page-numbered chunks.

PDFs are read page by page with pypdf (BSD licence; PyMuPDF extracts better but is AGPL).
Plain text and Markdown count as one page. Scanned PDFs have no text layer and are reported as such.
"""
import re
from dataclasses import dataclass
from pathlib import Path

MAX_WORDS = 300   # per chunk (about 400 tokens): small enough to retrieve precisely
MIN_WORDS = 40    # shorter pieces are merged with the previous chunk of the same page


@dataclass
class PageChunk:
    chunk_id: str
    page: int        # 1-based, as people say "page 17"
    position: int    # order in the document
    text: str        # header + body: what is searched and what the LLM reads
    body: str


def extract_pages(path: Path) -> list[str]:
    """Text of each page, in order. Empty strings for pages without a text layer."""
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        return [_clean(page.extract_text() or "") for page in reader.pages]
    return [_clean(path.read_text(encoding="utf-8", errors="replace"))]


def _clean(text: str) -> str:
    text = text.replace("\r", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)   # re-join words hyphenated across lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_pages(pages: list[str], file_id: str, filename: str) -> list[PageChunk]:
    """Split each page into chunks of at most MAX_WORDS, at paragraph and then sentence boundaries."""
    chunks: list[PageChunk] = []
    for page_no, page_text in enumerate(pages, start=1):
        if not page_text:
            continue
        pieces: list[str] = []
        for para in re.split(r"\n\s*\n", page_text):
            para = " ".join(para.split())
            if not para:
                continue
            words = para.split()
            if len(words) <= MAX_WORDS:
                pieces.append(para)
            else:  # long paragraph: split between sentences, then hard-split if needed
                current: list[str] = []
                for sentence in re.split(r"(?<=[.!?])\s+", para):
                    s_words = sentence.split()
                    while len(s_words) > MAX_WORDS:
                        pieces.append(" ".join(s_words[:MAX_WORDS]))
                        s_words = s_words[MAX_WORDS:]
                    if len(current) + len(s_words) > MAX_WORDS and current:
                        pieces.append(" ".join(current))
                        current = []
                    current += s_words
                if current:
                    pieces.append(" ".join(current))

        # Pack paragraphs together up to MAX_WORDS; never across pages, so citations stay exact.
        packed: list[str] = []
        for piece in pieces:
            if packed and len(packed[-1].split()) + len(piece.split()) <= MAX_WORDS:
                packed[-1] += "\n\n" + piece
            elif packed and len(piece.split()) < MIN_WORDS and len(packed[-1].split()) + len(piece.split()) <= MAX_WORDS * 1.2:
                packed[-1] += "\n\n" + piece
            else:
                packed.append(piece)

        for body in packed:
            chunks.append(PageChunk(
                chunk_id=f"{file_id}::{len(chunks):04d}",
                page=page_no,
                position=len(chunks),
                text=f"Document: {filename} | Page {page_no}\n\n{body}",
                body=body,
            ))
    return chunks
