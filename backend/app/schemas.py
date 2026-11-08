from typing import Literal

from pydantic import BaseModel, Field

Route = Literal["direct", "knowledge_base", "uploaded_file", "vision"]
FileKind = Literal["document", "image"]


class Citation(BaseModel):
    source: str                   # document title
    page: int | None = None
    snippet: str | None = None    # section name + start of the chunk
    index: int | None = None      # the [n] number used in the answer
    cited: bool = False           # did the answer actually cite it?
    doc_id: str | None = None


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[Message] = []
    user_role: str = "employee"
    file_id: str | None = None


class RouteDecision(BaseModel):
    route: Route
    reason: str


class ChatResponse(BaseModel):
    answer: str
    route: Route
    reason: str
    citations: list[Citation] = []
    confidence: Literal["high", "low", "abstained"] | None = None  # None when the gate is off
    retrieval_score: float | None = None                            # top reranker score, if reranking is on
    latency_ms: int | None = None
    timings_ms: dict[str, int] | None = None   # where the time went (observability)


class UploadedFile(BaseModel):
    file_id: str
    filename: str
    size: int
    kind: FileKind
    pages: int | None = None     # documents only
    chunks: int | None = None
    status: Literal["ready", "no_text", "stored"] = "stored"  # stored = image, not processed yet
