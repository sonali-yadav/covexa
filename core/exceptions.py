# This file stores exceptions that are used in the Covexa LLM module. 
# These exceptions are designed to handle various error scenarios that may arise when 
# interacting with the LLM API, such as temporary errors, authentication issues, and request errors. 
# Each exception class inherits from a base exception class, allowing for organized error 
# handling and categorization of different types of failures.

import logging
from time import time

import anthropic
import random

log = logging.getLogger("covexa.llm")

class LLMError(Exception):
    """Base class for every Covexa LLM failure."""

class LLMTemporaryError(LLMError):
    """Worth retrying: rate limit, server error, overloaded, timeout, network."""
    def __init__(self, message, *, status=None, retry_after=None):
        super().__init__(message)
        self.status = status
        self.retry_after = retry_after


def _classify(e: Exception) -> LLMError:
    """Classify and turn any SDK error into one of Covexa's three error types."""
    if isinstance(e, anthropic.APIConnectionError):
        return LLMTemporaryError(str(e))
    if isinstance(e, anthropic.APIStatusError):
        if e.status_code in RETRYABLE_STATUS:
            ra = e.response.headers.get("retry-after")
            return LLMTemporaryError(f"{e.status_code}: {str(e)}", status=e.status_code, 
                                     retry_after=float(ra) if ra else None)
        if e.status_code in (401, 403):
            return LLMAuthError(f"{e.status_code}: {str(e)}", status=e.status_code)
        return LLMRequestError(f"{e.status_code}: {str(e)}", status=e.status_code)
    raise e  # if not api error, then a bug in our code so let it crash and be fixed.

class LLMAuthError(LLMError):
    """Key or permission problem. Retrying won't help; alert whoever owns the key."""

class LLMRequestError(LLMError):
    """Our request is wrong (bad model, bad shape, too large). It's a bug, never retry."""

RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504, 529}


def _call(func, *, attempts=4, base=1.0, cap=20.0, **kwargs):
    """
    Call a function and handle exceptions, raising appropriate LLM exceptions.
    """
    for attempt in range(1, attempts + 1):
        try:
            return func(**kwargs)
        except (anthropic.APIConnectionError, anthropic.APIStatusError) as e:
            err = _classify(e)
            if isinstance(err, LLMTemporaryError) or attempt == attempts:
                raise err from e
            delay = err.retry_after or min(cap, base * 2 ** (attempt - 1)) * random.uniform(0.5, 1.5)
            log.warning("attempt %d/%d failed (%s); retrying in %.1fs", attempt, attempts, err, delay)
            time.sleep(delay)
