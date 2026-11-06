"""Questions about an uploaded document: answer from its own pages, citing page numbers."""
import re

from app.config import settings
from app.generation import llm
from app.ingestion import uploads_index
from app.schemas import ChatRequest, ChatResponse, Citation, RouteDecision, UploadedFile

SUMMARY = re.compile(r"\b(summar|overview|main points|key points|tl;?dr|what is this (document|file|report) about)",
                     re.IGNORECASE)

DOCUMENT_PROMPT = llm.GROUNDED_PROMPT.replace(
    "internal company documents", "a document the user uploaded"
).replace(
    "Before answering, check whether any source is about the specific thing the question asks about:\n"
    "the same document, project, customer, experiment or system. A source about a similar topic is not enough.\n\n",
    "The sources are excerpts of that one document, each labelled with its page number.\n"
    "When the user says 'this', 'it' or 'the document', they mean this document.\n\n",
)


def handle(req: ChatRequest, decision: RouteDecision, upload: UploadedFile) -> ChatResponse:
    if upload.status == "no_text":
        return ChatResponse(
            route=decision.route, reason=decision.reason + " The file has no extractable text.",
            confidence="abstained", citations=[Citation(source=upload.filename)],
            answer=f'"{upload.filename}" looks like a scanned document: it has no text layer I can read yet. '
                   "Reading scanned pages (OCR) is planned for a later version.")

    k = settings.top_k + 2  # a little more context than for the knowledge base: one document, fewer distractors
    whole = upload.chunks is not None and upload.chunks <= k
    if whole:
        chunks, how = uploads_index.first_chunks(upload.file_id, k), "The whole document was given to the model."
    elif SUMMARY.search(req.message):
        chunks, how = uploads_index.first_chunks(upload.file_id, k), \
            f"Summary based on the opening pages only ({upload.pages} pages in total)."
    else:
        chunks, how = uploads_index.search(upload.file_id, req.message, k), "Searched the document's pages."
        if not chunks:  # no keyword overlap at all: fall back to the opening pages
            chunks, how = uploads_index.first_chunks(upload.file_id, k), "No matching passage; used the opening pages."

    citations = [Citation(source=upload.filename, page=c["page"], index=i, snippet=c["body"][:200])
                 for i, c in enumerate(chunks, 1)]
    sources = "\n\n".join(f"[{i}] (page {c['page']}) {c['body']}" for i, c in enumerate(chunks, 1))
    answer = llm.chat(DOCUMENT_PROMPT, f"Sources:\n\n{sources}\n\nQuestion: {req.message}")

    confidence = "abstained" if llm.is_abstention(answer) else None
    for n in llm.cited_numbers(answer, len(citations)):
        citations[n - 1].cited = True
    return ChatResponse(answer=answer, route=decision.route, reason=f"{decision.reason} {how}",
                        citations=citations, confidence=confidence)
