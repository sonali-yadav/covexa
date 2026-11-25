# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

Early-stage project for learning the Claude API, with an insurance focus ("covexa"). Layout:

- `core/`: shared LLM helpers. `llm.py` wraps the Anthropic client (`ask`, `upload`, `ask_about_file`, `stream_answer`, all returning an `LLMResult`). `exceptions.py` maps SDK errors onto `LLMError` subclasses and handles retries with backoff. Ask before changing anything in `core/`.
- `config/`: Django project (settings, root URLconf, WSGI/ASGI).
- `ask/`: Django app mounted at `/ask/`. Right now it has only a placeholder `index` view.
- `first_call.py`: a single Messages API call that explains insurance concepts.
- `samples/make_policy.py`: generates a fictional sample policy PDF (`samples/motor_policy.pdf`).
- `scratch_day2.py`: throwaway experiments against `core`.

There is no test suite or linter config yet.

## Environment

- Python 3.14 virtualenv at `.venv/` (gitignored). Dependencies are pinned in `requirements.txt`.
- Secrets and config live in `.env` (gitignored) and are loaded with `load_dotenv()`. Django's `config/settings.py` loads it too.
  - `ANTHROPIC_API_KEY`: the SDK client reads this automatically.
  - `CLAUDE_MODEL`: optional model override for `first_call.py`. Defaults to `claude-haiku-5-5`.
  - `MODEL_FAST` / `MODEL_SMART` / `FILES_BETA`: model and beta overrides used by `core/llm.py`.
  - `DJANGO_SECRET_KEY`: required. Django won't start without it.
  - `DJANGO_DEBUG`: `True`/`False`. Defaults to `False`.
  - `DJANGO_ALLOWED_HOSTS`: comma-separated. Defaults to `localhost,127.0.0.1`.
- Database: SQLite at `db.sqlite3` (gitignored).
- VS Code is set up with `python.terminal.useEnvFile: true`, so terminals it opens also get the `.env` variables.

## Commands

```bash
source .venv/bin/activate
pip install -r requirements.txt   # recreate the env if .venv is missing
python manage.py migrate          # create/update db.sqlite3
python manage.py runserver        # http://localhost:8000/ask/
python manage.py check
python first_call.py              # makes one real (billed) API call
python samples/make_policy.py     # regenerates samples/motor_policy.pdf (fictional test document)
```

`samples/make_policy.py` embeds the macOS Georgia TTF because the built-in PDF fonts have no ₹ glyph. Off macOS it falls back to Helvetica and writes "Rs." instead. It exits with an error if the content no longer fits on exactly 3 pages.

## Conventions in existing code

- Pick models with `os.getenv(...)` and a default instead of hardcoding them.
- Scripts print `stop_reason` and `usage` next to the response text. Keep doing this so it's clear when a reply was truncated (`max_tokens`) and what it cost.
- Django settings come from environment variables via `.env`. Don't hardcode secrets or hosts in `config/settings.py`.
