# Contributing to hsg

Thanks for your interest in contributing! This guide covers the basics.

## Development setup

```bash
git clone https://github.com/davide/hsg.git
cd hsg
uv pip install -e ".[dev]"
pre-commit install
```

## Workflow

1. Fork the repo and create a branch from `main`.
2. Make your changes. Follow the existing code style (enforced by ruff).
3. Run the quality gate before committing:

   ```bash
   uv run ruff check .
   uv run ruff format --check .
   uv run mypy --strict hsg
   uv run pytest -q
   ```

4. Write tests for new functionality. Use the existing `tests/conftest.py`
   fixtures — do not open files under the real `assets/` directory in tests.
5. Commit using [Conventional Commits](https://www.conventionalcommits.org/)
   (e.g., `feat: add X`, `fix: handle Y`, `docs: update Z`).
6. Open a pull request. Fill in the PR template.

## Code style

- **Linter/formatter:** ruff (config in `pyproject.toml`).
- **Type checker:** mypy `--strict` — no `Any` without justification.
- **Tests:** pytest with `click.testing.CliRunner` for commands.
- **Logging** for diagnostics; `print`/`rich` only for user-facing output.
- **No comments** unless the code is genuinely non-obvious.

## Project structure

```
hsg/
  classes/     # Domain models (KnownSet, Frequency, SentenceCorpus, ...)
  commands/    # Click command implementations
  utils/       # I/O, writers, constants
  cli.py       # Click group + command registration
  __main__.py  # `python -m hsg` entry point
tests/         # Unit + command + snapshot tests
assets/        # Bundled corpora (do not modify in PRs)
```

## Adding a new KnownSet backend

1. Create `hsg/classes/<name>_knownset.py` with a class implementing `KnownSet`.
2. Register it in `hsg/classes/knownset_factory.py` (`create_known_set`).
3. Add the backend name to the `click.Choice` in each command that accepts
   `--known-set`.
4. Write unit tests in `tests/unit/test_<name>_knownset.py`.

## Adding a new Frequency corpus

1. Create `hsg/classes/<name>.py` with a class implementing `Frequency`.
2. Register it in `hsg/classes/frequency_factory.py` (`create_frequency`).
3. Add the corpus name to the `click.Choice` in each command that accepts
   `--frequencies-corpus`.
4. Write unit tests in `tests/unit/test_<name>.py`.

## Reporting issues

Use the issue templates in `.github/ISSUE_TEMPLATE/`. Include:
- `hsg --version` (or the git commit hash)
- Python version and OS
- The exact command you ran and the output
- What you expected vs. what happened
