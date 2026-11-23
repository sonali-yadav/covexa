# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

Early-stage project for learning the Claude API, with an insurance focus ("covexa"). So far there are two scripts: `first_call.py`, a single Messages API call that explains insurance concepts, and `samples/make_policy.py`, which generates a fictional sample policy PDF. There is no package structure, test suite, linter config, or dependency manifest yet.

`covexa/` is an empty, separately initialized git repo nested inside the top-level repo. Ask before putting code there or removing it.

## Environment

- Python 3.14 virtualenv at `.venv/` (gitignored). Installed packages: `anthropic`, `python-dotenv`, `reportlab`. There is no `requirements.txt` or `pyproject.toml` yet.
- Secrets and config live in `.env` (gitignored) and are loaded with `load_dotenv()`:
  - `ANTHROPIC_API_KEY`: the SDK client reads this automatically.
  - `CLAUDE_MODEL`: optional model override. Defaults to `claude-haiku-5-5`.
- VS Code is set up with `python.terminal.useEnvFile: true`, so terminals it opens also get the `.env` variables.

## Commands

```bash
source .venv/bin/activate
python first_call.py          # makes one real (billed) API call
python samples/make_policy.py # regenerates samples/motor_policy.pdf (fictional test document)
pip install anthropic python-dotenv reportlab   # recreate the env if .venv is missing
```

`samples/make_policy.py` embeds the macOS Georgia TTF because the built-in PDF fonts have no ₹ glyph. Off macOS it falls back to Helvetica and writes "Rs." instead. It exits with an error if the content no longer fits on exactly 3 pages.

## Conventions in existing code

- Pick the model with `os.getenv("CLAUDE_MODEL", <default>)` instead of hardcoding it.
- Scripts print `stop_reason` and `usage` next to the response text. Keep doing this so it's clear when a reply was truncated (`max_tokens`) and what it cost.
