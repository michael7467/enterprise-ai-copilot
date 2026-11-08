import logging
import time

from app.config import settings
from app.generation import llm
from app.retrieval.search import retriever
from app.schemas import ChatRequest, ChatResponse, Citation, RouteDecision

logger = logging.getLogger("janoai.kb")


def _ms_since(start: float) -> int:
    return round((time.perf_counter() - start) * 1000)


def handle(req: ChatRequest, decision: RouteDecision, upload=None) -> ChatResponse:
    start = time.perf_counter()
    result = retriever.search(req.message)
    timings = {"search_ms": _ms_since(start)}   # observability: where the time goes
    if not result.chunks:
        return ChatResponse(answer=llm.NOT_FOUND, route=decision.route, confidence="abstained",
                            reason=decision.reason + " No matching documents were found.", timings_ms=timings)

    citations = [Citation(source=c.title, snippet=f"{c.section}: {c.body[:200]}", index=i, doc_id=c.doc_id)
                 for i, c in enumerate(result.chunks, 1)]

    # Confidence gate (only when reranking is on: its score was calibrated in eval/generation/score_gate.py)
    confidence = None
    if result.top_score is not None:
        if result.top_score < settings.gate_threshold:
            logger.info("Gate: top score %.3f < %.2f, abstaining", result.top_score, settings.gate_threshold)
            return ChatResponse(
                answer=llm.NOT_FOUND, route=decision.route, citations=citations, confidence="abstained",
                retrieval_score=result.top_score, timings_ms=timings,
                reason=f"{decision.reason} Retrieval confidence too low ({result.top_score:.2f}), "
                       "so no answer was generated.")
        confidence = "high" if result.top_score >= settings.low_confidence else "low"

    question = f"Sources:\n\n{llm.sources_block([c.text for c in result.chunks])}\n\nQuestion: {req.message}"
    start = time.perf_counter()
    answer = llm.chat(llm.GROUNDED_PROMPT, question)
    timings["llm_ms"] = _ms_since(start)
    timings.update(llm.last_call_stats())   # Ollama's own split: loading, reading the prompt, writing
    if llm.is_abstention(answer):
        confidence = "abstained"
    for n in llm.cited_numbers(answer, len(citations)):
        citations[n - 1].cited = True

    return ChatResponse(answer=answer, route=decision.route, reason=decision.reason, citations=citations,
                        confidence=confidence, retrieval_score=result.top_score, timings_ms=timings)