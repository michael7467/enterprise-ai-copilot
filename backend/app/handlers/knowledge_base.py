"""Company knowledge base: retrieve -> confidence gate -> grounded answer with citations."""
import logging

from app.config import settings
from app.generation import llm
from app.retrieval.search import retriever
from app.schemas import ChatRequest, ChatResponse, Citation, RouteDecision

logger = logging.getLogger("janoai.kb")


def handle(req: ChatRequest, decision: RouteDecision, upload=None) -> ChatResponse:
    result = retriever.search(req.message)
    if not result.chunks:
        return ChatResponse(answer=llm.NOT_FOUND, route=decision.route, confidence="abstained",
                            reason=decision.reason + " No matching documents were found.")

    citations = [Citation(source=c.title, snippet=f"{c.section}: {c.body[:200]}", index=i, doc_id=c.doc_id)
                 for i, c in enumerate(result.chunks, 1)]

    # Confidence gate (only when reranking is on: its score was calibrated in eval/generation/score_gate.py)
    confidence = None
    if result.top_score is not None:
        if result.top_score < settings.gate_threshold:
            logger.info("Gate: top score %.3f < %.2f, abstaining", result.top_score, settings.gate_threshold)
            return ChatResponse(
                answer=llm.NOT_FOUND, route=decision.route, citations=citations, confidence="abstained",
                retrieval_score=result.top_score,
                reason=f"{decision.reason} Retrieval confidence too low ({result.top_score:.2f}), "
                       "so no answer was generated.")
        confidence = "high" if result.top_score >= settings.low_confidence else "low"

    question = f"Sources:\n\n{llm.sources_block([c.text for c in result.chunks])}\n\nQuestion: {req.message}"
    answer = llm.chat(llm.GROUNDED_PROMPT, question)
    if llm.is_abstention(answer):
        confidence = "abstained"
    for n in llm.cited_numbers(answer, len(citations)):
        citations[n - 1].cited = True

    return ChatResponse(answer=answer, route=decision.route, reason=decision.reason, citations=citations,
                        confidence=confidence, retrieval_score=result.top_score)
