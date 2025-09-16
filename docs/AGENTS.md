# Repository Guidelines

## Project Structure & Module Organization
- Entry points: `whisper_dictado.py` (CLI dictation), `web_server.py`/`start_web.py` (web UI), `configure_openrouter.py` (LLM config), `install.py` (guided setup).
- Packages: `utils/` (audio, VAD, text), `config/` (env loading and defaults), `web/` (`templates/`, `static/`).
- Tests/scripts: `test_setup.py`, `test_web_server.py`, `test_openrouter.py` in repo root.
- Config and examples: `config/config_template.env`, `openrouter_example.env`, `env_example.txt`. Runtime output goes to `output/` and `logs/`.

## Build, Test, and Development Commands
- Setup env: `python -m venv .venv` then `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows).
- Install deps: `pip install -r requirements.txt` or `python install.py` (installs deps, creates `.env` from template, makes folders).
- Run CLI: `python whisper_dictado.py [--llm-enable]`.
- Run web UI: `python web_server.py --host 127.0.0.1 --port 5000` then open the URL.
- Quick checks: `python test_setup.py`; with server running, `python test_web_server.py`; LLM check: `python test_openrouter.py`.

## Coding Style & Naming Conventions
- Python 3.8+, PEP 8, 4-space indentation; `snake_case` for files/functions/vars, `PascalCase` for classes, constants UPPER_CASE.
- Keep modules in `utils/` small and single‑purpose; avoid mixing server logic with templates under `web/`.
- Type hints and short docstrings for public functions; keep changes minimal and dependency‑light. No enforced formatter—follow existing style.

## Testing Guidelines
- Place lightweight tests/scripts as `test_*.py` in the repo root. Keep them deterministic and fast.
- Avoid network/API usage by default; mark optional LLM tests clearly. Clean up any artifacts written to `output/`.
- Run individually via `python test_setup.py` etc.

## Commit & Pull Request Guidelines
- Use clear, action‑oriented commit messages (prefer Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`).
- PRs must include: summary, rationale, before/after behavior, steps to verify, and any screenshots for web UI changes. Link related issues and update README when configs or UX change.

## Security & Configuration Tips
- Do not commit `.env` or keys. Start from `config/config_template.env` or `openrouter_example.env` and keep secrets local.
- Don’t commit large audio/log files; keep generated data in `output/` and `logs/`.
