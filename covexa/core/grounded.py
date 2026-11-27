import logging, os
from dataclasses import dataclass, field
from covexa.core.llm import client, _call, FILES_BETA, MODEL_SMART
from enum import StrEnum
from dotenv import load_dotenv


load_dotenv()
log = logging.getLogger("covexa.llm")
NOT_FOUND = "NOT_FOUND"

SYSTEM = f"""You are Covexa's policy assistant for a single customer's policy.
Rules:
- Answer ONLY from the policy document provided. Do not use general insurance knowledge.
- If the document does not contain the answer, reply with exactly {NOT_FOUND} and nothing else.
- Keep answers to 1-3 sentences, in plain English.
- Only state that something is covered if the document explicitly says so. Do not infer 
cover from general wording. If the document is silent on the specific item, 
reply NOT_FOUND.
-For questions with many items, list the 5 most important, then say how many more 
there are and offer to list them."""


class Status(StrEnum):
    ANSWERED = "answered"
    NOT_FOUND = "not_found"
    UNGROUNDED = "ungrounded"
    TRUNCATED = "truncated"


@dataclass
class Citation:
    quote: str
    page_from: int
    page_to: int


@dataclass
class GroundedAnswer:
    status: str  # "answered" | "not_found" | "ungrounded" | "truncated"
    text: str
    citations: list[Citation] = field(default_factory=list)


def answer_from_policy(file_id: str, question: str, *, title="Policy Document") -> GroundedAnswer:
    response = _call(
        client.beta.messages.create,
        model=MODEL_SMART, max_tokens=int(os.getenv("MAX_TOKENS", "1024")), betas=[FILES_BETA], system=SYSTEM,
        messages=[
            {"role": "user", "content": [
                {"type": "document", "source": {"type": "file", "file_id": file_id},
                 "title": title, "citations": {"enabled": True}},
                {"type": "text", "text": question},
            ]}
        ],
    )
    log.info("blocks=%s output_tokens=%d max=%d",
         [b.type for b in response.content], response.usage.output_tokens, 600)

    parts, cites = [], []
    for block in response.content:
        if block.type != "text":
            continue
        parts.append(block.text)
        for c in block.citations or []:
            if c.type == "page_location":
                cites.append(Citation(c.cited_text.strip(), 
                                      c.start_page_number, c.end_page_number - 1))
    text = "".join(parts).strip()

    # layer 3: deterministic check which won't trust the model's wording
    if response.stop_reason in ("max_tokens", "model_context_window_exceeded"):
        return GroundedAnswer(Status.TRUNCATED, text=text, citations=cites)
    if text.startswith(NOT_FOUND):
        return GroundedAnswer(Status.NOT_FOUND, text)
    if not cites:
        return GroundedAnswer(Status.UNGROUNDED, text)
    return GroundedAnswer(Status.ANSWERED, text, cites)
