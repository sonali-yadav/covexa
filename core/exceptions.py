# This file stores exceptions that are used in the Covexa LLM module. 
# These exceptions are designed to handle various error scenarios that may arise when 
# interacting with the LLM API, such as temporary errors, authentication issues, and request errors. 
# Each exception class inherits from a base exception class, allowing for organized error 
# handling and categorization of different types of failures.

import anthropic

class LLMError(Exception):
    """Base class for every Covexa LLM failure."""

class LLMTemporaryError(LLMError):
    """Worth retrying: rate limit, server error, overloaded, timeout, network."""

class LLMAuthError(LLMError):
    """Key or permission problem. Retrying won't help; alert whoever owns the key."""

class LLMRequestError(LLMError):
    """Our request is wrong (bad model, bad shape, too large). It's a bug, never retry."""

RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504, 529}


def _call(func, **kwargs):
    """
    Call a function and handle exceptions, raising appropriate LLM exceptions.
    """
    try:
        return func(**kwargs)
    except anthropic.APIConnectionError as e:  # network failure or timeout
        raise LLMTemporaryError(str(e)) from e
    except anthropic.APIStatusError as e:  # api answered with an error status code
        if e.status_code in RETRYABLE_STATUS:
            raise LLMTemporaryError(f"{e.status_code}: {str(e)}") from e
        if e.status_code in (401, 403):
            raise LLMAuthError(f"{e.status_code}: {str(e)}") from e
        raise LLMRequestError(f"{e.status_code}: {str(e)}") from e
