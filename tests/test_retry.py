# tests/test_retry.py
import anthropic, httpx, pytest
from covexa.core import llm, exceptions

def _status_error(code):
    req = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    return anthropic.APIStatusError("boom", response=httpx.Response(code, request=req), body=None)

def test_retries_temporary_then_succeeds(monkeypatch):
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    calls = {"n": 0}
    def flaky(**kw):
        calls["n"] += 1
        if calls["n"] < 3:
            raise _status_error(529)
        return "ok"
    assert exceptions._call(flaky) == "ok" and calls["n"] == 3

def test_never_retries_bad_request(monkeypatch):
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    calls = {"n": 0}
    def bad(**kw):
        calls["n"] += 1
        raise _status_error(400)
    with pytest.raises(exceptions.LLMRequestError):
        llm._call(bad)
    assert calls["n"] == 1