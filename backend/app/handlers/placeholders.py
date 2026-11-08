
from app.schemas import ChatRequest, ChatResponse, Citation, RouteDecision, UploadedFile


def vision(req: ChatRequest, decision: RouteDecision, upload: UploadedFile) -> ChatResponse:
    return ChatResponse(
        answer=f'Image questions are not available yet. "{upload.filename}" was received and stored.',
        route=decision.route, reason=decision.reason, citations=[Citation(source=upload.filename)])
