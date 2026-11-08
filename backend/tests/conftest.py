import pytest

from app.config import settings


@pytest.fixture(autouse=True)
def temporary_request_log(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "request_log", tmp_path / "logs" / "requests.jsonl")
