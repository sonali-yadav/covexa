import json
import os
from dataclasses import asdict
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from covexa.core.exceptions import LLMError, LLMTemporaryError
from covexa.core.llm import stream_answer
from covexa.core.grounded import answer_from_policy


SYSTEM = "You are Covexa, a helpful insurance assistant. Be concise."


def page(request):
    return render(request, "ask/page.html")


def sse(event: str, data) -> str:
    """Format a Server-Sent Event (SSE) message."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def policy_answer(request):
    q = request.GET.get("q", "").strip()
    ans = answer_from_policy(os.environ["COVEXA_SAMPLE_POLICY_FILE_ID"], q, title="Motor policy CVX-2026-0042")
    return JsonResponse(asdict(ans))


def stream(request):
    question = request.GET.get("q", "").strip()

    def events():
        try:
            for kind, payload in stream_answer([{"role": "user", "content": question}], system=SYSTEM, max_tokens=400):
                yield sse("delta" if kind == "text" else "done", payload)
        except LLMTemporaryError as e:
            yield sse("error", {"message": "Busy right now, please try again.", "retryable": True})
        except LLMError as e:
            yield sse("error", {"message": "Something went wrong on our side", "retryable": False})

    response = StreamingHttpResponse(events(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # to stop proxies like nginx from stream buffering
    return response
