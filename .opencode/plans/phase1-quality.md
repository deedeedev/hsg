# Phase 1 — Quality bar: detailed implementation plan

Goal: make the repo visibly engineered so a contributor judges it before
opening a PR. Adds ruff (lint+format), mypy strict, pytest, pre-commit, and
CI. No new features; existing behaviour is preserved and locked behind
tests.

Predecessor: `phase0-hygiene.md` (this phase builds on the post-Phase-0
`hsg/` package layout).
Branch: `phase1/quality` off `phase0/hygiene` (or off `main` once Phase 0
is merged — see "Branching note" below).
Estimated effort: 2-3 days.

---

## Branching note

Phase 0 is on `phase0/hygiene` and not yet merged. To keep this plan
independent, branch `phase1/quality` off `phase0/hygiene`. If Phase 0 is
merged to `main` first, branch off `main` instead. Either way, Phase 1
must not redo any Phase 0 work.

---

## 0. Conventions

- One commit per task group (see "Commit plan"). Conventional Commits.
- After every task group run: `uv run ruff check .`, `uv run mypy hsg`,
  `uv run pytest -q`. All three must pass before the next group.
- Do NOT change user-facing behaviour in this phase. If a test reveals a
  real bug, file it as a follow-up todo in code (`# TODO(phase2): ...`)
  and make the test assert the *current* behaviour so it stays green.
- Keep `scripts/heisigplecodict.py` out of mypy/pytest scope (it is a
  standalone script, not an installed module); exclude it explicitly.

---

## 1. Tooling setup

### 1.1 Expand the `dev` extra in `pyproject.toml`

Add ruff, pytest, pytest-cov, and pre-commit to `[project.optional-
dependencies].dev`:

```toml
dev = [
    "mypy>=1.0",
    "ruff>=0.6",
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pre-commit>=3.7",
    "types-tabulate",
    "types-requests",
]
```

Install with `uv pip install -e ".[dev]"` (note: `clipboard` is its own
extra; CI installs without it to prove the graceful-degrade guard).

### 1.2 Add tool config blocks to `pyproject.toml`

```toml
[tool.ruff]
line-length = 120
target-version = "py310"
extend-exclude = ["scripts", ".venv"]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "C4", "SIM"]
# E/F/W pycodestyle+pyflakes, I isort, UP pyupgrade,
# B bugbear, C4 comprehensions, SIM simplify

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["E501"]   # long assertion lines are fine in tests

[tool.ruff.format]
quote-style = "single"

[tool.mypy]
python_version = "3.10"
strict = true
warn_unused_ignores = true
warn_redundant_casts = true
# clipboard is an optional extra with no stubs; guard its import site
# instead of globally ignoring missing imports.
[[tool.mypy.overrides]]
module = "clipboard"
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"
filterwarnings = [
    "error::SyntaxWarning",
]

[tool.coverage.run]
source = ["hsg"]
branch = true

[tool.coverage.report]
show_missing = true
skip_covered = true
exclude_lines = ["if __name__ == .__main__.:", "if TYPE_CHECKING:"]
```

Rationale for `select`: a focused rule set the codebase can actually
satisfy. `target-version = "py310"` matches `requires-python`; ruff's
`UP` will rewrite `List[str]` -> `list[str]`, `Optional[X]` -> `X | None`
during the autofix pass in task 4.1.

---

## 2. Fix the mypy baseline (3 errors)

The default (non-strict) mypy run currently reports:

1. `hsg/utils/io.py:6` — `Cannot find implementation or library stub for
   module named "clipboard"`. Handled by the `[[tool.mypy.overrides]]`
   block above (module-level `ignore_missing_imports`). No code change.

2. `hsg/classes/ccedict.py:68-69` — `No overload variant of "__getitem__"
   of "list" matches argument type "str"`. Root cause: `frequencies` comes
   from `self.fq.find_word(...)` whose ABC signature
   (`hsg/classes/frequency.py:15`) is
   `find_word(self, word: str) -> Optional[list[Any]]`, but the data
   returned by `RenMinWang.find_word` / `SubtlexCh.find_word` is actually
   a `dict[str, Any]` (see `create_dict`). `frequencies['rank']` then
   indexes a list with a str.

   Fix: correct the `Frequency` ABC return types to
   `Optional[dict[str, Any]]` and propagate the annotation through
   `RenMinWang` and `SubtlexCh` (their `find_char`/`find_word` already
   return `self.chars.get(char)` / `self.words.get(word)`, which are
   dict values — the signatures were just wrong).

   ```python
   # hsg/classes/frequency.py
   from typing import Any
   from abc import ABCMeta, abstractmethod

   class Frequency(metaclass=ABCMeta):
       @abstractmethod
       def find_char(self, char: str) -> dict[str, Any] | None: ...
       @abstractmethod
       def find_word(self, word: str) -> dict[str, Any] | None: ...
   ```

   Update `heisig.py:36` (`frequency_data['rank']`) — same root cause,
   currently masked because `heisig.load_heisig` is untyped. Once
   `find_char` returns `dict | None`, the `frequency_data['rank'] if
   frequency_data else 9999` expression type-checks.

After this task: `uv run mypy hsg` (still default, not strict) is green.

---

## 3. Pre-commit hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9          # pin; bump in CI renovate/dependabot later
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.2
    hooks:
      - id: mypy
        additional_dependencies: [types-tabulate, types-requests]
        args: [--strict]
        exclude: ^scripts/
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: mixed-line-ending
        args: [--fix=lf]
```

`uv run pre-commit install` wires it into `.git/hooks/pre-commit`. The
hooks mirror CI so a clean local commit implies a green CI run.

---

## 4. Type hints end-to-end (mypy strict)

### 4.1 Ruff autofix pass first

Run `uv run ruff check --fix .` then `uv run ruff format .`. This rewrites
legacy typing (`List[str]` -> `list[str]`, `Optional[X]` -> `X | None`,
`Union[A, B]` -> `A | B`), removes unused imports, and normalises
formatting. Commit the result separately so the real type-fixing commit
stays reviewable.

Known unused imports to expect (ruff will remove): `Heisig` in
`frequencytools.py`, `lazy_pinyin` in `heisigtools.py`, `json`/`requests`
in `heisigtools.py` *only if* the `stories` Anki path is deleted — it is
not, so they stay. Let ruff decide; review the diff.

### 4.2 Annotate the untyped functions

Every `def` in `hsg/` needs `-> ReturnType` and typed parameters. The
current untyped surface (from `grep`):

- `hsg/classes/heisig.py` — `set_max_frame`, `load_heisig`,
  `get_known_frames`, `get_known_characters`, `is_known`,
  `is_additional_character`, `get_frame_info`, `get_statistics`,
  `output`, `__init__` (partially typed).
- `hsg/classes/hsk.py` — fully typed already except `__init__` (ok).
- `hsg/classes/renminwang.py` — `__init__`, `load_csv`, `create_dict`,
  `find_char`, `find_word`, `get_most_frequent_lemmas`.
- `hsg/classes/subtlexch.py` — `get_words_by_pos`,
  `get_most_frequent_lemmas` (partially), `__init__`.
- `hsg/classes/ccedict.py` — `sort_key` (returns `int`).
- `hsg/commands/*.py` — click command functions; annotate as
  `-> None` (click callbacks return None). `get_input` (in `io.py`) is
  already typed via the dedup but the return is `str`; tighten to `str`
  (it always returns a str or raises).

Target type hints (representative, not exhaustive — fill every signature):

```python
# heisig.py
def get_statistics(self, chars: list[str]) -> dict[str, Any]: ...
def get_frame_info(self, char: str) -> dict[str, Union[str, int]]: ...
def is_known(self, char: str) -> bool: ...
def output(self, words: list[dict[str, Any]], format: str) -> None: ...

# subtlexch.py / renminwang.py
def find_char(self, char: str) -> dict[str, Any] | None: ...
def get_most_frequent_lemmas(self, type: str = 'chars', num: int = -1,
    skip_heisig: bool = False, only_heisig: bool = False,
    min_length: int = 1, sort: str = 'rank', reverse: bool = False,
) -> list[dict[str, Any]]: ...
```

### 4.3 Tighten the ABCs and shared types

- `hsg/classes/frequency.py` — fixed in task 2.
- Introduce a shared type alias file `hsg/types.py` (or put it in
  `hsg/classes/__init__.py`) for the lemma record shape:
  `type Lemma = dict[str, Any]` and `type Frame = dict[str, str | int]`.
  Use across `heisig.py`, `ccedict.py`, frequency classes. This keeps
  `dict[str, Any]` from spreading untyped through the call graph.
- `hsg/utils/writers.py` — `Writer` ABC methods already annotated; make
  `WRITERS` typed as `dict[str, type[Writer]]` and `validate_fields`
  returns `list[str]`.

### 4.4 mypy strict gate

After 4.1-4.3, `uv run mypy --strict hsg` must report zero errors. Common
remaining issues to expect and fix:
- `click.UNPROCESSED` / `click.File` types — cast or use `Any` for the
  callback `fields` param in `parse`.
- `csv.DictReader` iterating as `dict[str, str]` — the `lemma['rank'] =
  idx + 1` writes in `renminwang.load_csv` need `# type: ignore[assignment]`
  or a typed wrapper (ruff/mypy flag int-vs-str in a str-valued dict; the
  clean fix is to store everything as `str` and convert at read sites —
  deferred to Phase 2, for now use a targeted `cast`).
- `re.Pattern` in `ccedict.get_query_type` — already annotated; the
  `ADDITIONAL_CHARACTERS.replace('[', '\[')` invalid-escape SyntaxWarning
  is fixed by ruff's `UP`/`W605` (rewrite as raw string `r'\['`).

---

## 5. Logging instead of print

### 5.1 Policy

- **User-facing output** (the data the command produces: tables, CSV,
  JSON, the enriched colourised text, the stories) stays on `print` via
  `rich` / `csv.writer(sys.stdout)`. This is the product, not a
  diagnostic.
- **Diagnostics** (progress, warnings, "loaded N entries", the Anki HTTP
  errors, the ccedict pickle build message) move to `logging`.

### 5.2 Setup

Add `hsg/logging_setup.py`:

```python
import logging

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
```

Each module that emits diagnostics gets `logger = get_logger(__name__)`.
Configure the root logger in `hsg/cli.py`:

```python
@click.group()
@click.option('-v', '--verbose', count=True, help='Increase log verbosity.')
def cli(verbose: int) -> None:
    level = logging.WARNING - 10 * verbose
    logging.basicConfig(level=max(level, logging.DEBUG), format='%(message)s')
```

This gives `hsg -v` -> INFO, `hsg -vv` -> DEBUG, default WARNING. Note
this **renames** the existing per-command `-v/--verbose` flags (which
currently print coverage stats). To avoid a CLI break in this phase,
keep the per-command `-v` behaviour as-is for `parse`/`enrich` and name
the group-level verbosity flag `-V/--verbose` (capital) or `--log-level`.
Pick `--log-level {error,warning,info,debug}` on the group to avoid
clashes; document in the commit. (Phase 3 README will formalise.)

### 5.3 Specific print -> logger conversions

- `ccedict.py` — the pickle build/load path has no print today; the
  `print('Error occurred ...')` in `tatoebasqlite.py` is in `scripts/`,
  out of scope.
- `heisigtools.stories` — Anki HTTP: currently no error handling; wrap
  `requests.request` in try/except and `logger.warning(...)` on failure
  instead of crashing. Keep the "NO HEISIG" line as user output.
- `heisigtools.parse`/`enrich` `-v` coverage stats — keep as `print`
  (user output), do not convert to logging.
- `hsk.py` `__main__` block — file is not run as a script anymore (Phase
  0 left it; the commented prints are dead). Remove the `if __name__ ==
  '__main__'` block in `hsk.py`, `subtlexch.py`, `renminwang.py` (dead
  scratch code). ruff's `F401`/`B015` will not catch it; do it manually.

---

## 6. Tests

### 6.1 Layout

```
tests/
    __init__.py
    conftest.py             # shared fixtures: tmp assets dir, tiny corpora
    unit/
        test_heisig.py
        test_hsk.py
        test_ccedict.py
        test_renminwang.py
        test_subtlexch.py
        test_writers.py
        test_io.py
    commands/
        test_parse.py
        test_enrich.py
        test_list.py
        test_stories.py     # Anki mocked
        test_sentences.py
        test_random.py
        test_lookup.py
        test_freq.py
    snapshots/
        test_output_formats.py
```

### 6.2 Fixtures (`conftest.py`)

- `tiny_assets` (session-scoped tmp dir) with miniature versions of the
  corpora so tests do not depend on the multi-MB `assets/`:
  - `heisig.tsv` with 10 frames (一..十).
  - `tatoeba.tsv` with 5 sentences.
  - `cedict_ts.u8` with 5 entries.
  - `hsk_new.csv` / `hsk_old.csv` with 5 rows each.
  - `subtlex-ch/` and `renminwang/` with 5 rows each.
  Monkeypatch `hsg.utils.constants.*` path constants to point at the tmp
  dir via a fixture, so no production asset is ever opened by the suite.
- `runner` — `click.testing.CliRunner` instance.
- `cli` — the `hsg.cli.cli` group, imported once.

### 6.3 Unit tests (one per class)

For each `classes/*` module, test the public methods against the tiny
fixtures. Representative assertions:

- `test_heisig.py`: `Heisig('subtlexch', 5).is_known('一')` is True;
  `.is_known('百')` is False; `get_statistics(['一','一','二'])` reports
  2 known of 3, frequency of '一' = 2 (66.67%).
- `test_hsk.py`: `get_hsk_new_char_level('爱')` returns the fixture
  level; `get_hsk_new_chars(1)` returns the level-1 subset.
- `test_ccedict.py`: `get_query_type('你好')` == 'simplified';
  `get_query_type('ni3')` == 'pinyin'; `get_query_type('hello')` ==
  'english'; `search(...)` filters by max_hsk. Use a fixture that
  forces the pickle path off (or pre-seeds it) so the test is fast.
- `test_renminwang.py` / `test_subtlexch.py`: `find_char`/`find_word`
  return the dict or None; `get_most_frequent_lemmas(num=2)` returns 2
  items sorted by rank; `only_heisig` filter narrows the set.
- `test_writers.py`: `CsvWriter`, `JsonWriter`, `TabulateWriter` each
  emit the expected string for a fixed input. `JsonWriter.writerows`
  emits valid JSON (regression test for the Phase 0 fix).
- `test_io.py`: `get_input('text', None)` returns the text; with no
  text and no stdin and no clipboard extra, raises `click.UsageError`.

### 6.4 Command tests (via `CliRunner`)

Each test invokes the group: `runner.invoke(cli, ['parse', '你好世界',
'-t', 'json'])` and asserts `result.exit_code == 0` and structural
properties of `result.output` (e.g. valid JSON for `-t json`; contains
the hanzi for `-t tabulate`; TSV header for `-t csv`).

- `test_parse.py`: csv/json/tabulate outputs; `--only-known` /
  `--only-unknown` filters; `--sort frame`; `--unique`; `-v` stats
  present.
- `test_enrich.py`: output contains rich markup (`[bold blue]`) for
  unknown frames.
- `test_list.py`: `--min 1 --max 5` returns 5 frames; `--sort
  frequency` ordering.
- `test_stories.py`: mock `requests.post` (use `monkeypatch` or
  `responses`/`pytest-httpserver` — prefer `monkeypatch` to avoid a new
  dep) to return a canned AnkiConnect payload; assert the story text is
  printed and HTML is stripped.
- `test_sentences.py` / `test_random.py`: `--max-frame 5` returns only
  sentences composed of the 5 known frames + additional chars; `random
  -n 2` returns 2 sentences (seed `random` via `monkeypatch.setattr
  ("random.sample", ...)` for determinism).
- `test_lookup.py`: query 'hello' returns english matches; `--max-hsk
  3` filters; `--exact`.
- `test_freq.py`: default returns ranked chars; `--only-heisig`
  narrows.

### 6.5 Snapshot tests (output formats)

A small, dedicated module that pins the exact bytes of `csv`/`json`/
`tabulate` output for a fixed input, using `pytest`'s plain `assert
output == expected` against committed `.txt` files in
`tests/snapshots/`. Avoids adding `pytest-syrupy` as a dep; review-by-
diff still works. If output drifts in Phase 2, update the snapshot
deliberately.

### 6.6 Coverage

`uv run pytest --cov=hsg --cov-report=term-missing`. Gate at 70% in CI
(see task 7). Target 85% by end of Phase 1; the command tests + unit
tests above should reach ~80% naturally. The uncovered tail will be the
Anki HTTP path in `stories` (mocked but branches) and `scripts/`.

---

## 7. CI (GitHub Actions)

Create `.github/workflows/ci.yml`:

```yaml
name: CI
on:
  push:
    branches: [main, "phase*"]
  pull_request:

jobs:
  lint-type-test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install uv
        run: pip install uv
      - name: Install package (no clipboard extra)
        run: uv pip install --system -e ".[dev]"
      - run: ruff check .
      - run: ruff format --check .
      - run: mypy --strict hsg
      - run: pytest --cov=hsg --cov-report=term --cov-fail-under=70
```

Notes:
- `uv pip install --system` avoids venv setup on the runner. Adjust for
  Windows if needed (uv handles it).
- **No `clipboard` extra installed** — proves the graceful-degrade
  import guard from Phase 0 works on CI. Command tests that need the
  clipboard fallback should be marked `@pytest.mark.skipif` or just
  exercise the text-argument path.
- `cov-fail-under=70` is the gate; raise to 85 before the v1.0 release.
- Add a separate `build` job (sdist + wheel via `uv build` or
  `python -m build`) to catch packaging regressions — this is a Phase 4
  concern but cheap to add now.

---

## 8. Commit plan

Order matters; each commit leaves `ruff && mypy && pytest` green.

1. `build(pyproject): add ruff, mypy, pytest, coverage, pre-commit config`
   - tool blocks + expanded `dev` extra; no source changes yet.
2. `fix(frequency): correct ABC return types (list -> dict | None)`
   - task 2; clears the ccedict mypy baseline.
3. `chore: add pre-commit hooks`
   - `.pre-commit-config.yaml`.
4. `style: ruff autofix and format pass`
   - task 4.1; the big mechanical rewrite (typing imports, formatting,
    raw strings for regex). Single commit so the noise is isolated.
5. `refactor: add type hints across hsg/`
   - task 4.2 + 4.3; mypy --strict goes green.
6. `refactor(logging): add log-level option and convert diagnostics`
   - task 5; introduces `hsg/logging_setup.py`, the group `--log-level`
    option, converts the Anki/parse diagnostic prints, removes dead
    `__main__` scratch blocks in classes.
7. `test: add pytest scaffold, unit and command tests`
   - task 6; the `tests/` tree + conftest fixtures. Coverage reaches
    the gate.
8. `ci: add GitHub Actions matrix (lint, type, test, coverage gate)`
   - task 7.

Commits 4 and 5 are the heaviest; 7 is the longest. If 4 produces a
huge diff, split it into one commit per subpackage
(`hsg/classes`, `hsg/commands`, `hsg/utils`) for reviewability.

---

## 9. Verification

Run from the repo root after the final commit:

```bash
# tooling
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict hsg
uv run pre-commit run --all-files

# tests + coverage
uv run pytest --cov=hsg --cov-report=term-missing --cov-fail-under=70

# behaviour smoke (unchanged from Phase 0)
.venv/bin/hsg parse "你好世界" -t json | python -m json.tool >/dev/null && echo "parse json OK"
.venv/bin/hsg lookup "你好" -m 2 -t tabulate | head -1   # header present
.venv/bin/hsg sentences "一" -m 5 -n 3 -t csv | head -1   # header present

# graceful degrade without clipboard extra
uv pip uninstall clipboard
.venv/bin/python -c "import hsg.cli" && echo "import OK without clipboard"
uv pip install -e ".[dev,clipboard]"
```

CI must be green on all 12 matrix cells (3 OS x 4 Python).

---

## 10. Acceptance criteria

- [ ] `ruff check .` and `ruff format --check .` exit zero.
- [ ] `mypy --strict hsg` exits zero.
- [ ] `pre-commit run --all-files` exits zero.
- [ ] `pytest --cov-fail-under=70` exits zero.
- [ ] The `Frequency` ABC returns `dict[str, Any] | None`, not
      `list[Any]`; `ccedict.py:68-69` and `heisig.py` frequency lookups
      type-check.
- [ ] Every `def` in `hsg/` has a return annotation and typed params.
- [ ] Dead `if __name__ == '__main__'` scratch blocks removed from
      `hsg.py`, `hsk.py`, `subtlexch.py`, `renminwang.py`.
- [ ] Diagnostics use `logging`; user-facing data still uses `print`/
      `csv.writer`.
- [ ] `tests/` covers each `classes/*` module and each `hsg` subcommand;
      snapshot tests pin csv/json/tabulate output.
- [ ] No test opens a file under the real `assets/` directory (fixtures
      monkeypatch the path constants).
- [ ] CI workflow runs on push and PR; matrix is Linux/macOS/Windows x
      Python 3.10-3.13; the `clipboard` extra is NOT installed in CI.
- [ ] `hsg parse/enrich/list/stories/sentences/random/lookup/freq`
      behaviour is unchanged (smoke commands produce the same output as
      at the end of Phase 0).

---

## 11. Out of scope for Phase 1

- Decoupling `KnownSet` from `Heisig`, the Anki optional plugin, the
  `SentenceCorpus` interface (Phase 2).
- README, LICENSE, CONTRIBUTING, docs site (Phase 3).
- PyPI release (Phase 4).
- Corpus downloader, Anki-deck export, i18n (Phase 5).
- Fixing the `tatoebasqlite.populate_db` SQLAlchemy bug (Phase 2; the
  file is in `scripts/` and excluded from mypy/pytest here).
- Replacing `dict[str, Any]` lemma records with a proper `dataclass`
  (Phase 2, when `KnownSet` is introduced — the `Lemma` type alias here
  is a stopgap).
- Renaming the per-command `-v/--verbose` flags (kept as-is to avoid a
  CLI break; revisit in Phase 3 when the README documents `--log-level`).
