"""Rule-based router: the baseline. Measure it on eval/router before replacing it with an LLM router."""
import re

from app.schemas import FileKind, RouteDecision

COMPANY_TERMS = re.compile(
    r"\b(our|we|policy|policies|company|leave|holiday|vacation|salary|payroll|expense|benefits?|hr|"
    r"onboarding|handbook|runbook|rollout|canary|incident|oncall|on-call|sla|slo|spec|roadmap|"
    r"customer|deploy(?:ment)?|release|internal|team)\b",
    re.IGNORECASE,
)


def route_message(message: str, file_kind: FileKind | None) -> RouteDecision:
    if file_kind == "image":
        return RouteDecision(route="vision", reason="An image is attached.")
    if file_kind == "document":
        return RouteDecision(route="uploaded_file", reason="A document is attached.")
    match = COMPANY_TERMS.search(message)
    if match:
        return RouteDecision(route="knowledge_base",
                             reason=f'Mentions a company-specific term: "{match.group(0)}".')
    return RouteDecision(route="direct", reason="General question; no company terms found.")
