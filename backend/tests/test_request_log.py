import json

from app.api.routes import log_request
from app.config import settings


def test_log_request_appends_one_json_line_per_call():
    log_request({"route": "knowledge_base", "latency_ms": 1200})
    log_request({"route": "direct", "question": "Perché?"})   # non-ASCII text is kept readable
    lines = settings.request_log.read_text(encoding="utf-8").splitlines()
    assert [json.loads(line) for line in lines] == [
        {"route": "knowledge_base", "latency_ms": 1200},
        {"route": "direct", "question": "Perché?"},
    ]


def test_log_request_never_breaks_an_answer(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "request_log", tmp_path)   # a folder, so writing fails
    log_request({"route": "direct"})                          # only a warning, no exception
