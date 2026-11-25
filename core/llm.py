import logging, mimetypes, time
from dataclasses import dataclass
from pathlib import Path

import anthropic
import os
from core.exceptions import LLMTemporaryError, _call, _classify
from dotenv import load_dotenv


load_dotenv()
log = logging.getLogger("covexa.llm")

MODEL_FAST = os.getenv("MODEL_FAST", "claude-haiku-5-5")
MODEL_SMART = os.getenv("MODEL_SMART", "claude-sonnet-5-5")
FILES_BETA = os.getenv("FILES_BETA", "files-api-2025-04-14")

client = anthropic.Anthropic(max_retries=0) # using custom retry logic so turn off default retries


@dataclass
class LLMResult:
    text: str
    stop_reason: str
    input_tokens: int
    output_tokens: int
    latency_ms: float

    @property
    def truncated(self) -> bool:
        return self.stop_reason in ("max_tokens", "model_context_window_exceeded")


def _to_result(response, started: float) -> LLMResult:
    text = "".join(block.text for block in response.content if block.type == "text")
    result = LLMResult(
        text=text,
        stop_reason=response.stop_reason,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        latency_ms=(time.perf_counter() - started) * 1000,
    )
    log.info("model=%s in=%d out=%d latency_ms=%.2f stop=%s", 
             response.model, result.input_tokens, result.output_tokens, result.latency_ms, result.stop_reason)
    return result


def ask(messages, *, system=None, model=MODEL_FAST, max_tokens=1024) -> LLMResult:
    """
    Ask a question to the LLM and return the result.
    """
    kwargs = {"model": model, "messages": messages, "max_tokens": max_tokens}
    if system:
        kwargs["system"] = system
    started = time.perf_counter()
    return _to_result(_call(client.messages.create, **kwargs), started=started)


def upload(path: str) -> str:
    p = Path(path)
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    with p.open("rb") as f:
        uploaded = _call(client.beta.files.upload, file=(p.name, f, mime))
    log.info("uploaded file=%s id=%s size=%d mime=%s", p.name, uploaded.id, uploaded.size_bytes, mime)
    return uploaded.id


def ask_about_file(file_id: str, question: str, * , model=MODEL_FAST, max_tokens=1024) -> LLMResult:
    """
    Ask a question about a file and return the result.
    """
    started = time.perf_counter()
    response = _call(client.beta.messages.create,
        model=model, max_tokens=max_tokens, messages= [
        {"role": "user", "content": [ # document should come before question recommended as a good practice
            {"type": "document", "source": {"type": "file", "file_id": file_id}},
            {"type": "text", "text": question},
        ]}
    ], betas=[FILES_BETA])
    return _to_result(response, started=started)


def stream_answer(messages, *, system=None, model=MODEL_FAST, max_tokens=1024):
    """Yields ("text", str) pieces, then exactly one ("done", dict)."""
    kwargs = {"model": model, "messages": messages, "max_tokens": max_tokens}
    if system:
        kwargs["system"] = system
    
    stream = _call(client.messages.create, **kwargs)
    input_tokens, output_tokens, stop_reason = 0, 0, None
    try:
        for event in stream:
            log.debug("event: %s", event.type)
            if event.type == "message_start":
                input_tokens = event.message.usage.input_tokens
            elif event.type == "content_block_delta" and event.delta.type == "text_delta":
                yield ("text", event.delta.text)
            elif event.type == "message_delta":
                stop_reason = event.message.stop_reason
                output_tokens = event.message.usage.output_tokens
            elif event.type == "message_stop":
                yield ("done", {
                    "stop_reason": stop_reason,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "truncated": stop_reason in ("max_tokens", "model_context_window_exceeded"),
                })
                return
    except (anthropic.APIConnectionError, anthropic.APIStatusError) as e:
        raise _classify(e) from e  # mid-stream error, no silent retry
    raise LLMTemporaryError("stream ended without message_stop event")
    
    
    
    started = time.perf_counter()
    for event in _call(client.messages.stream, **kwargs):
        if event.type == "response.output_text.delta":
            yield ("text", event.delta)
        elif event.type == "response.completed":
            result = LLMResult(
                text="",
                stop_reason=event.stop_reason,
                input_tokens=event.usage.input_tokens,
                output_tokens=event.usage.output_tokens,
                latency_ms=(time.perf_counter() - started) * 1000,
            )
            log.info("model=%s in=%d out=%d latency_ms=%.2f stop=%s", 
                     event.model, result.input_tokens, result.output_tokens, result.latency_ms, result.stop_reason)
            yield ("done", result)