# Phase 0 — Hygiene: detailed implementation plan

Goal: make the repo installable, internally consistent, and free of dead
code. No new features. After this phase `uv pip install -e .` works, one
`hsg` command exposes every subcommand, and no dead module imports remain.

Predecessor: `v1.0-publishable-release.md` (this phase refines the Phase 0
section of that document).
Estimated effort: 1-2 days.

---

## 0. Conventions

- Branch: `phase0/hygiene` off `main`.
- One commit per task group (see "Commit plan" at the bottom). Conventional
  Commits style (`chore:`, `refactor:`, `build:`).
- Run `python -m hsg --help` after every task group to confirm the CLI still
  loads.
- If a task touches a Python module, re-run any smoke tests added in this
  phase (see "Verification").
- Do NOT add tests, linter config, or CI in this phase — those are Phase 1.
  This phase only deletes, fixes, and reorganises existing code.

---

## 1. Purge dead and broken code

### 1.1 Delete `utils/statistics.py`

Why: imports a `HeisigTools` symbol that does not exist in `heisigtools`
(the module exports `cli`, `stories`, `parse`, `enrich`, `list`, `gui`,
`get_input`). Importing this module raises `ImportError`. It is not imported
by any other file.

Steps:
- `git rm utils/statistics.py`

Verify: `grep -r "from utils.statistics\|import statistics" --include=*.py`
returns nothing.

### 1.2 Delete `pysimpleguitable.py`

Why: a PySimpleGUI sandbox that demonstrates the `Table` element. Not
registered as an entry point, not imported anywhere, not documented.

Steps:
- `git rm pysimpleguitable.py`

### 1.3 Remove the `gui` stub from `heisigtools.py`

Why: `heisigtools.gui` is a placeholder ("aaa" text, one Ok / Quit button)
that does nothing useful and pulls PySimpleGUI into the import graph of the
main CLI.

Steps:
- Delete the `gui` function and its `@cli.command()` decorator in
  `heisigtools.py` (currently `heisigtools.py:281-299`).
- Remove the `import PySimpleGUI as sg` import
  (`heisigtools.py:12`) and the unused `from PySimpleGUI.PySimpleGUI import
  theme_previewer` (`heisigtools.py:5`).
- Remove `pysimplegui` from the Pipfile and from `pyproject.toml` deps (see
  task 4.1).

### 1.4 Remove unused / wrong imports

Files to audit (fix in place, do not move anything):

- `heisigtools.py`
  - Remove `from ast import Try` (line 1) — unused, wrong import.
  - Remove `from io import StringIO` and the `HTMLParser`/`MLStripper` block
    ONLY IF we decide to keep the `stories` Anki path as-is; we keep it for
    now. Just remove the unused `StringIO` import if `MLStripper` is the only
    user — check first. (`StringIO` IS used inside `MLStripper`; leave it.)
  - Remove `import json` and `import requests` only if `stories` is removed
    in this phase. We keep `stories` as-is in Phase 0 (it is decoupled in
    Phase 2), so leave them.
  - Remove `from rich import print` only after confirming no other code in
    the module uses `print` as the rich instance. The `enrich`, `stories`
    and `parse --verbose` blocks all use `print` from rich. Leave it.
- `frequencytools.py`
  - Remove `import sys` (line 1, unused — the module writes via `csv.writer`
    to `sys.stdout`, so `sys` IS used; double-check before removing. Actually
    `sys.stdout` is referenced on line 38; keep `import sys`.)
  - Re-audit after the CLI consolidation; some imports become unused once
    `get_input` is deduplicated.
- `tatoebasqlite.py`
  - Remove `from os import sep` (line 2, unused).
- `writers.py`
  - `JsonWriter.writerow` calls `json.dumps(row)` without printing — this
    is a bug. Fix the method to print the JSON:
    `print(json.dumps(row))`.
  - `JsonWriter.writerows` uses bare `print(rows)` — that prints the Python
    repr, not JSON. Fix to `print(json.dumps(rows))`.

### 1.5 Remove the stale `build/` and `hsg.egg-info/` directories

Why: generated artifacts, already in `.gitignore` (`hsg.egg-info`). The
`build/` directory is not ignored and contains stale `bdist.linux-x86_64`
output.

Steps:
- `git rm -r build/`
- `rm -rf hsg.egg-info/` (it is gitignored, no `git rm` needed — but verify
  with `git status`).
- Add `build/` to `.gitignore`.

---

## 2. Fix packaging metadata

### 2.1 Fix `setup.py` typo

`setup.py:5` currently has `versio='0.1.0'`. Change to `version='0.1.0'`.

This file is replaced by `pyproject.toml` in task 4.1, so this fix is mostly
to avoid leaving a broken file behind during the transition. If you do the
`pyproject.toml` migration first and delete `setup.py`, this task is moot —
either order is fine, just do both before the commit.

### 2.2 Deduplicate the Pipfile entries

`Pipfile:12-13` currently declares both `ht` and `hsg` as editable installs
pointing at `.`. That is redundant and one of the names (`ht`) does not match
`setup.py`. This is fixed by task 4.3 (Pipfile removal). Until then, remove
the `ht` line so only `hsg = {editable = true, path = "."}` remains.

---

## 3. Consolidate the CLIs

### 3.1 Design

Replace the four entry points

```
hsg          = heisigtools:cli
hsg-tatoeba  = heisigtatoeba:cli
hsg-cc       = ccedictsearch:search
hsg-freq     = frequencytools:search
```

with one `click.Group` named `cli` in a new top-level module `cli.py` (or
keep it in `heisigtools.py` — see 3.3) exposing subcommands:

```
hsg parse      # from heisigtools.parse
hsg enrich     # from heisigtools.enrich
hsg list       # from heisigtools.list
hsg stories    # from heisigtools.stories
hsg sentences  # from heisigtatoeba.sentences
hsg random     # from heisigtatoeba.random_sentences
hsg lookup     # from ccedictsearch.search
hsg freq       # from frequencytools.search
```

Rationale: matches the existing TODO at `heisigtools.py:21`; one command is
discoverable; no risk of namespace collisions on PyPI.

### 3.2 Steps

1. Create `hsg/cli.py` (package layout — see task 4.1) with:

   ```python
   import click
   from hsg.commands import (
       heisigtools, heisigtatoeba, ccedictsearch, frequencytools,
   )

   @click.group()
   def cli():
       pass

   cli.add_command(heisigtools.parse)
   cli.add_command(heisigtools.enrich)
   cli.add_command(heisigtools.list)
   cli.add_command(heisigtools.stories)
   cli.add_command(heisigtatoeba.sentences)
   cli.add_command(heisigtatoeba.random_sentences)
   cli.add_command(ccedictsearch.search)
   cli.add_command(frequencytools.search)
   ```

   (Use `@cli.command()` import style if you prefer — either works. The
   point is one group, four modules contributing commands.)

2. In each existing module, remove the `@click.group()` decorator and the
   `if __name__ == "__main__": cli()` block (or keep the latter for direct
   execution — optional). The command functions themselves stay unchanged.

3. Update `entry_points` / `[project.scripts]` in `pyproject.toml` to a
   single entry:

   ```toml
   [project.scripts]
   hsg = "hsg.cli:cli"
   ```

4. Delete the old entry points from `setup.py` (or delete `setup.py`
   entirely — see 4.1).

### 3.3 Rename conflict note

`heisigtools.py` currently defines both the `cli` group and the `parse` /
`enrich` subcommands. When you move the group to `hsg/cli.py`, keep the
subcommands in `hsg/commands/heisigtools.py` and rename the module if you
prefer (e.g. `hsg/commands/text.py` for `parse`/`enrich`, `hsg/commands/
frames.py` for `list`, `hsg/commands/stories.py` for `stories`). Naming is
not important in Phase 0; pick the lowest-friction option (keep the four
filenames as-is inside `hsg/commands/`).

### 3.4 Deduplicate `get_input`

`heisigtools.py:265` and `frequencytools.py:47` define identical `get_input`
helpers. Extract one copy into `hsg/utils/io.py` (a renamed `utils/io.py`)
and import from both call sites. Do not change behaviour.

---

## 4. Migrate to `pyproject.toml` (PEP 621)

### 4.1 New package layout

Move from flat-layout to src-free package layout (no `src/` directory, but a
single top-level package `hsg/`):

```
hsg/
    __init__.py
    __main__.py          # new: enables `python -m hsg`
    cli.py               # new: the click.Group
    commands/
        __init__.py
        heisigtools.py
        heisigtatoeba.py
        ccedictsearch.py
        frequencytools.py
    classes/
        __init__.py
        heisig.py
        ccedict.py
        hsk.py
        frequency.py
        renminwang.py
        subtlexch.py
    utils/
        __init__.py
        constants.py
        io.py            # renamed from writers.py + new get_input
        writers.py
        heisigplecodict.py   # the standalone Pleco builder script
    assets/              # moved from top-level assets/
```

Keep `heisigplecodict.py` as a standalone script under `hsg/utils/` OR move
it to `scripts/` at the repo root — it is not a CLI command and should not
be on the install path. Pick `scripts/heisigplecodict.py` for clarity; it
imports from `hsg.classes` so it has access to the package.

The `assets/` directory stays at the repo root for now (the corpus builder
that downloads them is Phase 5). `utils/constants.py` already resolves paths
relative to `__file__`, so the move of `classes/` and `utils/` into `hsg/`
changes the absolute path resolution. Verify and, if needed, update
`ASSETS_DIR_PATH` in `utils/constants.py` to walk up one more directory
level.

### 4.2 `pyproject.toml`

Create `pyproject.toml` (PEP 621) with `hatchling` as build backend:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "hsg"
version = "0.1.0"
description = "Analyse Chinese text against your known-character set and mine comprehensible example sentences."
readme = "README.md"
requires-python = ">=3.10"
license = { text = "Apache-2.0" }
authors = [{ name = "Davide" }]
dependencies = [
    "click>=8.0",
    "rich>=12.0",
    "tabulate>=0.9",
    "pypinyin>=0.44",
    "requests>=2.28",
]

[project.optional-dependencies]
clipboard = ["clipboard>=0.0.4"]
anki = []  # anki integration runs via AnkiConnect HTTP; no extra package
dev = [
    "mypy>=1.0",
    "types-tabulate",
    "types-requests",
]

[project.scripts]
hsg = "hsg.cli:cli"

[tool.hatch.build.targets.wheel]
packages = ["hsg"]

[tool.hatch.build.targets.wheel.force-include]
"assets" = "hsg/assets"
```

Notes:
- Drop `pysimplegui` (no more GUI).
- Drop `sqlalchemy` (the Tatoeba SQLite work is not wired up; revisit in
  Phase 2). If you would rather keep the dependency to avoid breaking
  `tatoebasqlite.py`, leave it in `dev` — but the file is being moved under
  `scripts/`, not imported at runtime.
- `clipboard` becomes an optional extra because it is a thin platform
  wrapper; the module should degrade gracefully (try/except ImportError
  with a warning) when the extra is missing. Phase 0 only needs to mark it
  optional; the graceful-degrade fix can ride with the move.

### 4.3 Drop `Pipfile` and `Pipfile.lock`

Replace with a `uv`-managed environment:

```bash
uv venv
uv pip install -e ".[dev]"
```

Commit a `uv.lock` once `uv pip compile` produces a stable lock. Do not
commit the old `Pipfile.lock`.

### 4.4 Delete `setup.py`

Once `pyproject.toml` is in place and `uv pip install -e .` works, delete
`setup.py`. The `pyproject.toml` `[build-system]` table supersedes it.

### 4.5 `__main__.py`

Create `hsg/__main__.py`:

```python
from hsg.cli import cli

if __name__ == "__main__":
    cli()
```

This enables `python -m hsg ...`.

---

## 5. Update imports across the moved files

After task 4.1 every module is under `hsg/`. Update internal imports:

- `from classes.heisig import Heisig` -> `from hsg.classes.heisig import Heisig`
- `from utils.constants import ...` -> `from hsg.utils.constants import ...`
- etc.

Use a one-shot codemod:

```bash
# from the repo root, after the move
grep -rl "^from classes\.\|^from utils\.\|^import classes\.\|^import utils\." hsg/ scripts/
# then sed -i 's/^from classes\./from hsg.classes./; ...' on each hit
```

(You may use `ruff` or `python -m libcst` — but Phase 0 keeps deps minimal,
so a `sed` one-liner is acceptable.)

Verify: `python -c "import hsg; import hsg.cli"` from the repo root exits
zero with no output.

---

## 6. Fix `setup.py`-era bugs discovered during the move

- `tatoebasqlite.py:42` calls `sql.insert(self.ZH_EN)` passing the string
  table name where SQLAlchemy expects a `Table` object. The `create_db_
  tables` method already builds and returns the `Table` but never stores it
  on `self`; `populate_db` cannot reuse it. This is a real bug but the file
  is being demoted to `scripts/` and not wired into any CLI in Phase 0.
  Add a `# BUG: populate_db reuses a table name string; fix in Phase 2`
  comment and leave the logic for now. Phase 2 (decouple) will rewrite it
  behind the `SentenceCorpus` interface.

---

## 7. Commit plan

Group the work into these commits, in order. Each commit must leave the tree
installable and `python -m hsg --help` functional (from commit 5 onward).

1. `chore: remove broken statistics.py and sandbox pysimpleguitable.py`
2. `chore: drop build/ artifacts and ignore build/`
3. `refactor(heisigtools): remove unused gui stub and stale imports`
   - removes `gui`, `PySimpleGUI` imports, `from ast import Try`
4. `fix(writers): make JsonWriter actually emit JSON`
5. `refactor: move source into hsg/ package and update imports`
   - the big move; one commit so reviewers see the relocation clearly
6. `build: replace setup.py and Pipfile with PEP 621 pyproject.toml`
   - new `pyproject.toml`, new `hsg/__main__.py`, single `hsg` entry point,
     deletes `setup.py`, `Pipfile`, `Pipfile.lock`
7. `refactor(cli): consolidate four entry points into one hsg command`
   - new `hsg/cli.py`, removes `@click.group()` from the four modules,
     deduplicates `get_input` into `hsg/utils/io.py`
8. `chore: move heisigplecodict.py to scripts/`

After commit 8 the Phase 0 acceptance criteria should all pass.

---

## 8. Verification

Run from the repo root after each commit, and again at the end:

```bash
# 1. No dead imports of removed modules
grep -rn "from utils.statistics\|pysimpleguitable\|from ast import Try" \
    --include=*.py . || echo OK

# 2. Module imports cleanly
uv pip install -e ".[dev]"
python -c "import hsg, hsg.cli, hsg.commands, hsg.classes, hsg.utils" && echo OK

# 3. CLI loads and lists every subcommand
hsg --help
# expected subcommands: parse, enrich, list, stories, sentences, random,
# lookup, freq

# 4. No leftover entry points
grep -n "hsg-tatoeba\|hsg-cc\|hsg-freq" pyproject.toml setup.py 2>/dev/null \
    || echo OK   # (setup.py should not exist by now)

# 5. JsonWriter emits JSON
python - <<'PY'
from hsg.utils.writers import JsonWriter
w = JsonWriter(['a','b'])
w.writerow([1, 'x'])          # expect a JSON object on stdout
w.writerows([[1,'x'],[2,'y']])  # expect a JSON array on stdout
PY

# 6. Asset paths still resolve (constants moved with the package)
python - <<'PY'
from hsg.utils.constants import HEISIG_CSV, CCEDICT_CSV, TATOEBA_CSV
import os
for p in (HEISIG_CSV, CCEDICT_CSV, TATOEBA_CSV):
    assert os.path.isfile(p), f"missing asset: {p}"
print("assets OK")
PY
```

---

## 9. Acceptance criteria

- [ ] `utils/statistics.py` is gone; nothing imports it.
- [ ] `pysimpleguitable.py` is gone.
- [ ] `build/` is gone and ignored.
- [ ] `heisigtools.gui` is gone; `PySimpleGUI` is not imported anywhere in
      the package.
- [ ] `from ast import Try` is gone.
- [ ] `JsonWriter.writerow` / `writerows` emit valid JSON.
- [ ] Source lives under `hsg/`; every internal import is `from hsg.*`.
- [ ] `pyproject.toml` (PEP 621, hatchling) drives the build; `setup.py`
      and `Pipfile*` are gone.
- [ ] `requires-python = ">=3.10"`; `pysimplegui`, `sqlalchemy` are no
      longer runtime deps.
- [ ] `hsg` is the sole entry point; `hsg-tatoeba`, `hsg-cc`, `hsg-freq`
      are gone.
- [ ] `hsg --help` lists: `parse`, `enrich`, `list`, `stories`,
      `sentences`, `random`, `lookup`, `freq`.
- [ ] `python -m hsg --help` works.
- [ ] `heisigplecodict.py` lives in `scripts/` and is not importable from
      the package.
- [ ] All bundled asset files (heisig.tsv, cedict_ts.u8, tatoeba.tsv,
      hsk_*.csv, renminwang/, subtlex-ch/) are found by `constants.py`
      after the package restructure.

---

## 10. Out of scope for Phase 0

- Adding tests, ruff, mypy, pre-commit, CI (Phase 1).
- Decoupling `KnownSet` from `Heisig`, the AnkiConnect optional plugin,
  the `SentenceCorpus` interface (Phase 2).
- README, LICENSE, CONTRIBUTING, docs site (Phase 3).
- PyPI release, Homebrew, AUR (Phase 4).
- Corpus downloader, Anki-deck export, i18n extensions (Phase 5).
- Fixing the `tatoebasqlite.populate_db` SQLAlchemy bug (Phase 2, when the
  file is rewritten).
