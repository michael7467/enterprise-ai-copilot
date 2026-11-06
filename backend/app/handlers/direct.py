"""General questions: the language model answers on its own, with the recent conversation as context."""
from app.generation import llm
from app.schemas import ChatRequest, ChatResponse, RouteDecision

HISTORY_TURNS = 6  # last messages passed to the model


def handle(req: ChatRequest, decision: RouteDecision, upload=None) -> ChatResponse:
    history = [m.model_dump() for m in req.history[-HISTORY_TURNS:]]
    answer = llm.chat(llm.DIRECT_PROMPT, req.message, history=history)
    return ChatResponse(answer=answer, route=decision.route, reason=decision.reason)
