# Phase 2 — Decouple from Heisig: detailed implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make "given a text, what % can I read" work for any known-character source — Heisig, HSK, a user file, an Anki export — not just Heisig frames.

**Architecture:** Introduce a `KnownSet` ABC mirroring the existing `Frequency` ABC. `Heisig` becomes one `KnownSet` backend; `HSK` and `file` backends follow. A `SentenceCorpus` ABC decouples sentence loading from known-set filtering. Anki stories move to a one-shot importer that writes JSON; `hsg stories` reads from disk.

**Tech Stack:** Python >=3.10, click, rich, pypinyin, pytest, mypy --strict, ruff.

Predecessor: `phase1-quality.md` (complete — ruff/mypy/pytest/pre-commit/CI all green).
Branch: `phase2/decouple` off `main`.
Estimated effort: 3-5 days.

---

## 0. Conventions

- One commit per task group (see "Commit plan" at the end). Conventional Commits.
- After every task group run: `uv run ruff check .`, `uv run ruff format --check .`,
  `uv run mypy --strict hsg`, `uv run pytest -q`. All four must pass.
- TDD: write the test first, watch it fail, implement, watch it pass, commit.
- Do NOT remove existing CLI flags in this phase — add `--known-set` alongside
  `--max-frame`, keep `--max-frame` as a deprecated alias that maps to
  `--known-set heisig --max <value>`. Remove `--max-frame` in a future phase.
- Update `tests/conftest.py` fixtures as needed for new backends.
- `scripts/` is excluded from ruff/mypy/pytest.

---

## 1. KnownSet ABC

### 1.1 Create `hsg/classes/knownset.py`

The ABC mirrors `Frequency` but for "which characters does the learner know".
It absorbs `get_statistics` (currently on `Heisig`, but only calls `is_known`)
and the `ADDITIONAL_CHARACTERS` allowlist logic.

**Files:**
- Create: `hsg/classes/knownset.py`
- Test: `tests/unit/test_knownset.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_knownset.py
from hsg.classes.knownset import KnownSet
from hsg.utils.constants import ADDITIONAL_CHARACTERS


class DummyKnownSet(KnownSet):
    def __init__(self, chars: set[str]) -> None:
        self._chars = chars

    def is_known(self, char: str) -> bool:
        return char in self._chars or char in ADDITIONAL_CHARACTERS

    def get_known_characters(self) -> list[str]:
        return list(self._chars) + list(ADDITIONAL_CHARACTERS)

    def get_char_info(self, char: str) -> dict[str, Any]:
        return {'char': char}


from typing import Any  # noqa: E402


class TestKnownSetABC:
    def test_is_known(self):
        ks = DummyKnownSet({'一', '二'})
        assert ks.is_known('一') is True
        assert ks.is_known('三') is False
        assert ks.is_known('!') is True  # additional

    def test_is_additional_character(self):
        ks = DummyKnownSet(set())
        assert ks.is_additional_character('!') is True
        assert ks.is_additional_character('一') is False

    def test_get_statistics(self):
        ks = DummyKnownSet({'一', '二'})
        stats = ks.get_statistics(['一', '一', '二', '三'])
        assert stats['chars'] == 4
        assert stats['known'] == 3
        assert stats['unknown'] == 1
        assert stats['known_percent'] == 75.0

    def test_get_statistics_empty(self):
        ks = DummyKnownSet(set())
        stats = ks.get_statistics([])
        assert stats['chars'] == 0
        assert stats['known_percent'] == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_knownset.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'hsg.classes.knownset'`

- [ ] **Step 3: Write minimal implementation**

```python
# hsg/classes/knownset.py
from abc import ABCMeta, abstractmethod
from typing import Any

from hsg.utils.constants import ADDITIONAL_CHARACTERS


class KnownSet(metaclass=ABCMeta):
    """ABC for 'which characters does the learner know'.

    Backends: Heisig (frame range), HSK (level cap), file (user list),
    anki-export (Anki deck export).
    """

    @abstractmethod
    def is_known(self, char: str) -> bool:
        """Return True if the learner knows this character."""
        raise NotImplementedError

    @abstractmethod
    def get_known_characters(self) -> list[str]:
        """Return the full list of known characters (excluding ADDITIONAL)."""
        raise NotImplementedError

    def is_additional_character(self, char: str) -> bool:
        """Return True if char is a non-Hanzi allowlist character."""
        return char in ADDITIONAL_CHARACTERS

    def get_char_info(self, char: str) -> dict[str, Any]:
        """Return backend-specific metadata for a character.

        Heisig returns {frame, keyword, pinyin, frequency}.
        HSK returns {level}. File returns {char}.
        Override in subclasses.
        """
        return {'char': char}

    def get_statistics(self, chars: list[str]) -> dict[str, Any]:
        """Compute coverage statistics for a list of characters.

        This is a concrete method — it only calls is_known(), so it
        works for any KnownSet backend.
        """
        unique_chars = [c for i, c in enumerate(chars) if c not in chars[:i]]
        total_chars = len(chars)
        total_chars_unique = len(unique_chars)
        total_known = len([c for c in chars if self.is_known(c)])
        total_known_unique = len([c for c in unique_chars if self.is_known(c)])
        total_known_percent = round(total_known / total_chars * 100, 2) if total_chars > 0 else 0
        total_known_unique_percent = (
            round(total_known_unique / total_chars_unique * 100, 2) if total_chars_unique > 0 else 0
        )
        frequencies: dict[str, dict[str, Any]] = {}
        for c in chars:
            if c not in frequencies:
                frequencies[c] = {'occurrencies': 1, 'percent': None}
            else:
                frequencies[c]['occurrencies'] += 1
        for c in frequencies:
            frequencies[c]['percent'] = round(frequencies[c]['occurrencies'] / len(chars) * 100, 2)
        return {
            'chars': total_chars,
            'known': total_known,
            'known_percent': total_known_percent,
            'unknown': total_chars - total_known,
            'unknown_percent': round(100 - total_known_percent, 2),
            'chars_unique': total_chars_unique,
            'known_unique': total_known_unique,
            'known_unique_percent': total_known_unique_percent,
            'unknown_unique': total_chars_unique - total_known_unique,
            'unknown_unique_percent': round(100 - total_known_unique_percent, 2),
            'frequencies': frequencies,
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_knownset.py -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Lint + typecheck**

Run: `ruff check --fix . && ruff format . && mypy --strict hsg`
Expected: 0 errors.

---

## 2. Heisig KnownSet adapter

Refactor `Heisig` to implement `KnownSet`. The existing API stays — we just
inherit from the ABC and move `get_statistics` to the base class.

### 2.1 Make `Heisig` extend `KnownSet`

**Files:**
- Modify: `hsg/classes/heisig.py`
- Modify: `tests/unit/test_heisig.py`

- [ ] **Step 1: Add test for KnownSet inheritance**

```python
# Append to tests/unit/test_heisig.py

def test_heisig_is_knownset(patched_constants):
    from hsg.classes.knownset import KnownSet
    h = Heisig('subtlexch', 5)
    assert isinstance(h, KnownSet)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_heisig.py::test_heisig_is_knownset -v`
Expected: FAIL — `AssertionError: assert False is True` (Heisig doesn't subclass KnownSet yet)

- [ ] **Step 3: Modify Heisig to extend KnownSet**

In `hsg/classes/heisig.py`:

```python
# Add import at top
from hsg.classes.knownset import KnownSet

# Change class declaration
class Heisig(KnownSet):

    # Remove get_statistics method — it's now inherited from KnownSet.
    # Remove is_additional_character — it's now inherited from KnownSet.

    # get_known_characters stays (it's abstract on KnownSet).
    # get_known_frames stays (Heisig-specific).
    # is_known stays (it's abstract on KnownSet).
    # get_frame_info becomes the override of get_char_info:

    def get_char_info(self, char: str) -> dict[str, Any]:
        """Return Heisig frame info for a character."""
        return self.heisig[char]

    # Keep get_frame_info as an alias for backward compat:
    def get_frame_info(self, char: str) -> dict[str, Any]:
        return self.get_char_info(char)
```

Key changes:
1. Add `from hsg.classes.knownset import KnownSet` to imports.
2. Change `class Heisig:` → `class Heisig(KnownSet):`.
3. **Delete** the `get_statistics` method body (lines 62-95) — inherited from KnownSet.
4. **Delete** the `is_additional_character` method — inherited from KnownSet.
5. Add `get_char_info` override (delegates to `self.heisig[char]`).
6. Keep `get_frame_info` as an alias calling `self.get_char_info(char)`.
7. Keep `output` (Heisig-specific formatter, not on the ABC).

- [ ] **Step 4: Run all heisig tests**

Run: `pytest tests/unit/test_heisig.py tests/unit/test_knownset.py -v`
Expected: PASS (all tests).

- [ ] **Step 5: Run full test suite**

Run: `pytest tests/ -q`
Expected: 70+ tests pass (existing tests must not regress).

- [ ] **Step 6: Lint + typecheck + commit**

```bash
ruff check --fix . && ruff format . && mypy --strict hsg
git add hsg/classes/knownset.py hsg/classes/heisig.py tests/unit/test_knownset.py tests/unit/test_heisig.py
git commit -m "refactor(knownset): add KnownSet ABC, make Heisig implement it"
```

---

## 3. HSK KnownSet backend

### 3.1 Create `hsg/classes/hsk_knownset.py`

Wraps the existing `HSK` class to implement `KnownSet`. "Known" = all chars
at or below a given HSK level.

**Files:**
- Create: `hsg/classes/hsk_knownset.py`
- Test: `tests/unit/test_hsk_knownset.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_hsk_knownset.py
from hsg.classes.hsk_knownset import HSKKnownSet


class TestHSKKnownSet:
    def test_is_known(self, patched_constants):
        ks = HSKKnownSet(max_level=2)
        assert ks.is_known('一') is True   # level 1
        assert ks.is_known('四') is True   # level 2
        assert ks.is_known('十') is False  # not in fixture

    def test_is_known_additional(self, patched_constants):
        ks = HSKKnownSet(max_level=1)
        assert ks.is_known('!') is True

    def test_get_known_characters(self, patched_constants):
        ks = HSKKnownSet(max_level=1)
        chars = ks.get_known_characters()
        assert '一' in chars
        assert '!' in chars  # ADDITIONAL_CHARACTERS

    def test_get_char_info(self, patched_constants):
        ks = HSKKnownSet(max_level=3)
        info = ks.get_char_info('一')
        assert info['level'] == '1'

    def test_get_statistics(self, patched_constants):
        ks = HSKKnownSet(max_level=1)
        stats = ks.get_statistics(['一', '二', '四'])
        assert stats['chars'] == 3
        assert stats['known'] == 2  # 一,二 are level 1; 四 is level 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_hsk_knownset.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# hsg/classes/hsk_knownset.py
from typing import Any

from hsg.classes.hsk import HSK
from hsg.classes.knownset import KnownSet
from hsg.utils.constants import ADDITIONAL_CHARACTERS


class HSKKnownSet(KnownSet):
    """KnownSet backed by HSK levels.

    A character is 'known' if its HSK new-list level <= max_level,
    or if it's in ADDITIONAL_CHARACTERS.
    """

    def __init__(self, max_level: int = 6, use_old: bool = False) -> None:
        self.hsk = HSK()
        self.max_level = max_level
        self.use_old = use_old
        self._known_chars: set[str] = set(self._compute_known_chars())

    def _compute_known_chars(self) -> list[str]:
        if self.use_old:
            chars = self.hsk.get_hsk_old_chars()
            return [c for c in chars if int(self.hsk.get_hsk_old_char_level(c) or 99) <= self.max_level]
        chars = self.hsk.get_hsk_new_chars()
        return [c for c in chars if int(self.hsk.get_hsk_new_char_level(c) or 99) <= self.max_level]

    def is_known(self, char: str) -> bool:
        return char in self._known_chars or char in ADDITIONAL_CHARACTERS

    def get_known_characters(self) -> list[str]:
        return list(self._known_chars) + list(ADDITIONAL_CHARACTERS)

    def get_char_info(self, char: str) -> dict[str, Any]:
        if self.use_old:
            level = self.hsk.get_hsk_old_char_level(char)
        else:
            level = self.hsk.get_hsk_new_char_level(char)
        return {'char': char, 'level': level or ''}
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/unit/test_hsk_knownset.py -v`
Expected: PASS (5 tests).

- [ ] **Step 5: Lint + typecheck + commit**

```bash
ruff check --fix . && ruff format . && mypy --strict hsg
git add hsg/classes/hsk_knownset.py tests/unit/test_hsk_knownset.py
git commit -m "feat(knownset): add HSK KnownSet backend"
```

---

## 4. File KnownSet backend

### 4.1 Create `hsg/classes/file_knownset.py`

Reads a user-supplied file (one hanzi per line) and uses that as the known set.

**Files:**
- Create: `hsg/classes/file_knownset.py`
- Test: `tests/unit/test_file_knownset.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_file_knownset.py
from hsg.classes.file_knownset import FileKnownSet


class TestFileKnownSet:
    def test_load_file(self, tmp_path):
        f = tmp_path / 'known.txt'
        f.write_text('一\n二\n三\n')
        ks = FileKnownSet(str(f))
        assert ks.is_known('一') is True
        assert ks.is_known('二') is True
        assert ks.is_known('四') is False

    def test_is_known_additional(self, tmp_path):
        f = tmp_path / 'known.txt'
        f.write_text('一\n')
        ks = FileKnownSet(str(f))
        assert ks.is_known('!') is True

    def test_get_known_characters(self, tmp_path):
        f = tmp_path / 'known.txt'
        f.write_text('一\n二\n')
        ks = FileKnownSet(str(f))
        chars = ks.get_known_characters()
        assert '一' in chars
        assert '!' in chars

    def test_get_statistics(self, tmp_path):
        f = tmp_path / 'known.txt'
        f.write_text('一\n二\n')
        ks = FileKnownSet(str(f))
        stats = ks.get_statistics(['一', '二', '三'])
        assert stats['chars'] == 3
        assert stats['known'] == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_file_knownset.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# hsg/classes/file_knownset.py
from typing import Any

from hsg.classes.knownset import KnownSet
from hsg.utils.constants import ADDITIONAL_CHARACTERS


class FileKnownSet(KnownSet):
    """KnownSet backed by a user-supplied file (one character per line)."""

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self._chars: set[str] = set()
        with open(filepath) as f:
            for line in f:
                char = line.strip()
                if char and len(char) == 1:
                    self._chars.add(char)

    def is_known(self, char: str) -> bool:
        return char in self._chars or char in ADDITIONAL_CHARACTERS

    def get_known_characters(self) -> list[str]:
        return list(self._chars) + list(ADDITIONAL_CHARACTERS)

    def get_char_info(self, char: str) -> dict[str, Any]:
        return {'char': char, 'known': char in self._chars}
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/unit/test_file_knownset.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Lint + typecheck + commit**

```bash
ruff check --fix . && ruff format . && mypy --strict hsg
git add hsg/classes/file_knownset.py tests/unit/test_file_knownset.py
git commit -m "feat(knownset): add file-based KnownSet backend"
```

---

## 5. KnownSet factory

### 5.1 Create `hsg/classes/knownset_factory.py`

Centralises the `{'heisig': Heisig, 'hsk': HSKKnownSet, ...}[name]()` dispatch
pattern (currently duplicated 3× for Frequency). Returns a `KnownSet` instance.

**Files:**
- Create: `hsg/classes/knownset_factory.py`
- Test: `tests/unit/test_knownset_factory.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_knownset_factory.py
import pytest

from hsg.classes.knownset import KnownSet
from hsg.classes.knownset_factory import create_known_set


class TestKnownSetFactory:
    def test_create_heisig(self, patched_constants):
        ks = create_known_set('heisig', max=5, frequencies_corpus='subtlexch')
        assert isinstance(ks, KnownSet)
        assert ks.is_known('一') is True

    def test_create_hsk(self, patched_constants):
        ks = create_known_set('hsk', max=2)
        assert isinstance(ks, KnownSet)
        assert ks.is_known('一') is True

    def test_create_file(self, tmp_path):
        f = tmp_path / 'known.txt'
        f.write_text('一\n')
        ks = create_known_set('file', filepath=str(f))
        assert isinstance(ks, KnownSet)
        assert ks.is_known('一') is True

    def test_invalid_backend(self):
        with pytest.raises(ValueError):
            create_known_set('bad-backend')
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_knownset_factory.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# hsg/classes/knownset_factory.py
from typing import Any

from hsg.classes.knownset import KnownSet


def create_known_set(
    backend: str,
    *,
    max: int = -1,
    frequencies_corpus: str = 'subtlexch',
    filepath: str | None = None,
    **kwargs: Any,
) -> KnownSet:
    """Create a KnownSet instance by backend name.

    Args:
        backend: 'heisig', 'hsk', or 'file'.
        max: Frame limit (heisig) or HSK level cap (hsk). -1 = all.
        frequencies_corpus: Frequency corpus for heisig backend.
        filepath: Path to known-characters file (required for 'file').
    """
    if backend == 'heisig':
        from hsg.classes.heisig import Heisig

        return Heisig(frequencies_corpus, max)

    if backend == 'hsk':
        from hsg.classes.hsk_knownset import HSKKnownSet

        level = max if max > 0 else 6
        return HSKKnownSet(max_level=level)

    if backend == 'file':
        from hsg.classes.file_knownset import FileKnownSet

        if not filepath:
            raise ValueError("backend 'file' requires filepath")
        return FileKnownSet(filepath)

    raise ValueError(f'unknown known-set backend: {backend}')
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/unit/test_knownset_factory.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Lint + typecheck + commit**

```bash
ruff check --fix . && ruff format . && mypy --strict hsg
git add hsg/classes/knownset_factory.py tests/unit/test_knownset_factory.py
git commit -m "feat(knownset): add factory for KnownSet backends"
```

---

## 6. Refactor `parse` and `enrich` to use KnownSet

### 6.1 Add `--known-set` option to `parse`

Add `--known-set {heisig,hsk,file}` and `--max` alongside the existing
`--max-frame` (kept as deprecated alias). When `--known-set` is not given,
default to `heisig` (preserving current behaviour).

**Files:**
- Modify: `hsg/commands/heisigtools.py` (parse command, ~lines 111-166)
- Modify: `tests/commands/test_parse.py`

- [ ] **Step 1: Add test for `--known-set hsk`**

```python
# Append to tests/commands/test_parse.py

def test_parse_known_set_hsk(patched_constants, runner, app):
    result = runner.invoke(app, ['parse', '一二四', '--known-set', 'hsk', '--max', '1', '-t', 'json'])
    assert result.exit_code == 0
    data = json.loads(result.output.strip())
    # 一,二 are HSK level 1 (known); 四 is level 2 (unknown)
    known_chars = [d for d in data if d['known'] != '*']
    unknown_chars = [d for d in data if d['known'] == '*']
    assert any(d['hanzi'] == '一' for d in known_chars)
    assert any(d['hanzi'] == '四' for d in unknown_chars)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/commands/test_parse.py::test_parse_known_set_hsk -v`
Expected: FAIL — `no such option: --known-set`

- [ ] **Step 3: Modify parse command**

In `hsg/commands/heisigtools.py`, modify the `parse` function:

Add these options after `--max-frame`:

```python
@click.option(
    '--known-set',
    type=click.Choice(['heisig', 'hsk', 'file']),
    default=None,
    help='Known-character source (default: heisig).',
)
@click.option(
    '--known-file',
    type=click.Path(exists=True),
    default=None,
    help='Path to known-characters file (for --known-set file).',
)
@click.option(
    '--max',
    'max_known',
    type=click.INT,
    default=None,
    help='Max frame/level for known-set (overrides --max-frame).',
)
```

In the function body, replace the direct `Heisig(...)` instantiation with:

```python
from hsg.classes.knownset_factory import create_known_set

# Determine known-set backend
ks_backend = known_set or 'heisig'
ks_max = max_known if max_known is not None else max_frame

if ks_backend == 'file':
    if not known_file:
        raise click.UsageError('--known-set file requires --known-file')
    hsg = create_known_set('file', filepath=known_file)
else:
    hsg = create_known_set(ks_backend, max=ks_max, frequencies_corpus=frequencies_corpus)
```

Then replace `hsg.is_known(c)` calls — they already work because `KnownSet`
defines `is_known`. Replace `hsg.is_additional_character(c)` — inherited from
`KnownSet`. Replace `hsg.get_statistics(chars)` — inherited.

For the frame-info access (`hsg.get_frame_info(x)`, `hsg.heisig`), use
`hsg.get_char_info(x)` and check via `isinstance(hsg, Heisig)` or try/except
KeyError — but the cleaner approach: use `get_char_info` which returns `{}`
for unknown chars on non-Heisig backends. The `frame` and `frequency` columns
will be empty for non-Heisig backends, which is correct.

Update the data-building loop:

```python
# Replace hsg.get_frame_info(char) with:
info = hsg.get_char_info(char) if char in known_set_chars else {}

# Where known_set_chars is built once:
if hasattr(hsg, 'heisig'):
    known_set_chars = set(hsg.heisig.keys())
else:
    known_set_chars = set(hsg.get_known_characters())
```

Actually, simpler: the `char in hsg.heisig` check becomes a try/except or
isinstance check. But for backward compat, `Heisig.get_char_info` raises
`KeyError` for unknown chars (same as `get_frame_info`). For `HSKKnownSet`
and `FileKnownSet`, `get_char_info` always returns a dict. So:

```python
# For the "is this a known-set character" branch:
try:
    info = hsg.get_char_info(char)
    has_info = True
except KeyError:
    info = {}
    has_info = False
```

This preserves the current Heisig behaviour (KeyError → non-Heisig branch)
and works for HSK/File (always returns info).

- [ ] **Step 4: Run tests**

Run: `pytest tests/commands/test_parse.py -v`
Expected: PASS (all parse tests including the new one).

- [ ] **Step 5: Run full suite + lint + commit**

```bash
pytest tests/ -q
ruff check --fix . && ruff format . && mypy --strict hsg
git add hsg/commands/heisigtools.py tests/commands/test_parse.py
git commit -m "feat(parse): add --known-set option for pluggable backends"
```

### 6.2 Add `--known-set` option to `enrich`

Same pattern. Enrich currently hardcodes `'subtlexch'` for the frequency corpus.

**Files:**
- Modify: `hsg/commands/heisigtools.py` (enrich command, ~lines 241-278)
- Modify: `tests/commands/test_enrich.py`

- [ ] **Step 1: Add test**

```python
# Append to tests/commands/test_enrich.py

def test_enrich_known_set_hsk(patched_constants, runner, app):
    result = runner.invoke(app, ['enrich', '一二四', '--known-set', 'hsk', '--max', '1'])
    assert result.exit_code == 0
    assert '一' in result.output
    assert '四' in result.output
```

- [ ] **Step 2: Run to verify fail, then implement**

Add the same `--known-set` / `--known-file` / `--max` options to `enrich`.
Replace `Heisig('subtlexch', max_frame)` with the factory call.
Replace `char in hsg.heisig` with `isinstance(hsg, Heisig) and char in hsg.heisig`
or a `hasattr` check — for non-Heisig backends, "unknown Heisig frame" (blue)
vs "non-Heisig char" (red) distinction doesn't apply; all unknowns are red.

```python
for char in chars:
    if not hsg.is_known(char):
        if hasattr(hsg, 'heisig') and char in hsg.heisig:
            print(f'[bold blue]{char}[/bold blue]', end='')
        else:
            print(f'[bold red]{char}[/bold red]', end='')
    else:
        print(f'[bold white]{char}[/bold white]', end='')
```

- [ ] **Step 3: Run tests + lint + commit**

```bash
pytest tests/commands/test_enrich.py -v
ruff check --fix . && ruff format . && mypy --strict hsg
git add hsg/commands/heisigtools.py tests/commands/test_enrich.py
git commit -m "feat(enrich): add --known-set option for pluggable backends"
```

---

## 7. Refactor `sentences` and `random` to use KnownSet

### 7.1 Decouple `TatoebaHeisig` from Heisig

`TatoebaHeisig` currently re-parses `heisig.tsv` to build the "allowed
characters" set. Replace this with a `KnownSet` parameter.

**Files:**
- Modify: `hsg/commands/heisigtatoeba.py`
- Modify: `tests/commands/test_sentences.py`
- Modify: `tests/commands/test_random.py`

- [ ] **Step 1: Add test for `--known-set hsk` on sentences**

```python
# Append to tests/commands/test_sentences.py

def test_sentences_known_set_hsk(patched_constants, runner, app):
    result = runner.invoke(app, ['sentences', '一', '--known-set', 'hsk', '--max', '2', '-f', 'json'])
    assert result.exit_code == 0
    data = json.loads(result.output.strip(), strict=False)
    assert len(data) > 0
```

- [ ] **Step 2: Run to verify fail**

Run: `pytest tests/commands/test_sentences.py::test_sentences_known_set_hsk -v`
Expected: FAIL — `no such option: --known-set`

- [ ] **Step 3: Modify `TatoebaHeisig` to accept a `KnownSet`**

Change `__init__` to accept `known_set: KnownSet` instead of
`heisigcsv: str, maxframe: int`:

```python
class TatoebaHeisig:
    def __init__(self, tatoebacsv: str, known_set: KnownSet) -> None:
        self.tatoebacsv = tatoebacsv
        self.known_set = known_set
        self.tatoeba: dict[str, list[str]] = {}
        self.allowed_sentences: list[Sentence] = []

    def get_allowed_characters(self) -> list[str]:
        return self.known_set.get_known_characters()

    def get_all_allowed_sentences(self) -> None:
        self.load_tatoeba()
        allowed = set(self.get_allowed_characters())
        for sentence in self.tatoeba:
            if all(char in allowed for char in sentence):
                self.allowed_sentences.append(
                    {'hanzi': sentence, 'translations': self.tatoeba[sentence]}
                )
```

Remove `load_heisig`, `get_allowed_frames`, `self.heisig`, `self.maxframe`.

Update the `sentences` and `random` CLI commands to use the factory:

```python
@click.option('--known-set', type=click.Choice(['heisig', 'hsk', 'file']), default=None)
@click.option('--known-file', type=click.Path(exists=True), default=None)
@click.option('--max', 'max_known', type=click.INT, default=None)
@click.option('-m', '--max-frame', type=click.INT, default=-1)
@click.option('-a', '--all-characters', is_flag=True, default=False)
def sentences(keyword, max_frame, all_characters, known_set, known_file, max_known, ...):
    if all_characters:
        # Use a permissive KnownSet that knows everything
        from hsg.classes.file_knownset import FileKnownSet
        import tempfile
        # Or: create an "AllKnownSet" that returns True for everything
        ks = create_known_set('heisig', max=-1, frequencies_corpus='subtlexch')
    else:
        ks_backend = known_set or 'heisig'
        ks_max = max_known if max_known is not None else max_frame
        if ks_backend == 'file':
            ks = create_known_set('file', filepath=known_file)
        else:
            ks = create_known_set(ks_backend, max=ks_max, frequencies_corpus='subtlexch')
    ht = TatoebaHeisig(TATOEBA_CSV, ks)
    ...
```

- [ ] **Step 4: Update existing tests**

The existing `sentences`/`random` tests use `-m 5` (max-frame) and `-a`
(all-characters). These should still work because `--max-frame` is kept as
a deprecated alias that maps to `--known-set heisig --max <value>`.

The `random` tests already use `-a` (all-characters). With the refactor,
`-a` creates a Heisig KnownSet with `max=-1` (all frames known), which
allows all sentences. This preserves the current behaviour.

- [ ] **Step 5: Run tests + lint + commit**

```bash
pytest tests/commands/test_sentences.py tests/commands/test_random.py -v
ruff check --fix . && ruff format . && mypy --strict hsg
git add hsg/commands/heisigtatoeba.py tests/commands/test_sentences.py tests/commands/test_random.py
git commit -m "refactor(sentences): decouple TatoebaHeisig from Heisig, use KnownSet"
```

---

## 8. Rename Frequency ABC Heisig-specific params

### 8.1 Rename `skip_heisig`/`only_heisig` → `skip_known`/`only_known`

The `Frequency.get_most_frequent_lemmas` and both implementations
(`RenMinWang`, `SubtlexCh`) open `HEISIG_CSV` directly to filter by Heisig
characters. This should accept a `known_characters: set[str]` parameter
instead.

**Files:**
- Modify: `hsg/classes/frequency.py`
- Modify: `hsg/classes/renminwang.py`
- Modify: `hsg/classes/subtlexch.py`
- Modify: `hsg/commands/frequencytools.py`
- Modify: `tests/unit/test_subtlexch.py`
- Modify: `tests/unit/test_renminwang.py`
- Modify: `tests/commands/test_freq.py`

- [ ] **Step 1: Update tests to use new param names**

In `tests/unit/test_subtlexch.py`, change:
```python
# Old:
lemmas = s.get_most_frequent_lemmas(only_heisig=True)
# New:
from hsg.utils.constants import ADDITIONAL_CHARACTERS
known = set('一二三四五六七八九十')
lemmas = s.get_most_frequent_lemmas(only_known=known)
```

Same in `tests/unit/test_renminwang.py`.

In `tests/commands/test_freq.py`, change:
```python
# Old:
runner.invoke(app, ['freq', '...', '-o', '-t', 'json'])
# New:
runner.invoke(app, ['freq', '...', '--only-known', '-t', 'json'])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/test_subtlexch.py tests/unit/test_renminwang.py tests/commands/test_freq.py -v`
Expected: FAIL — `TypeError: unexpected keyword argument 'only_known'`

- [ ] **Step 3: Update the ABC and implementations**

In `hsg/classes/frequency.py`, change `get_most_frequent_lemmas` signature:

```python
def get_most_frequent_lemmas(
    self,
    type: str = 'chars',
    num: int = -1,
    skip_known: set[str] | None = None,
    only_known: set[str] | None = None,
    min_length: int = 1,
    sort: str = 'rank',
    reverse: bool = False,
) -> list[dict[str, Any]]:
    raise NotImplementedError
```

Replace `skip_heisig`/`only_heisig` (booleans) with `skip_known`/`only_known`
(`set[str] | None`). When `skip_known` is provided, filter out those chars.
When `only_known` is provided, keep only those chars. When both are None, no
filtering. This eliminates the `xor` logic and the `HEISIG_CSV` import.

In `hsg/classes/subtlexch.py` and `hsg/classes/renminwang.py`, update
`get_most_frequent_lemmas`:

```python
def get_most_frequent_lemmas(
    self,
    type: str = 'chars',
    num: int = -1,
    skip_known: set[str] | None = None,
    only_known: set[str] | None = None,
    min_length: int = 1,
    sort: str = 'rank',
    reverse: bool = False,
) -> list[dict[str, Any]]:
    lemmas = self.char_freq if type == 'chars' else self.word_freq
    if num == -1:
        num = len(lemmas)
    if skip_known is not None:
        lemmas = [l for l in lemmas if l['lemma'] not in skip_known]
    if only_known is not None:
        lemmas = [l for l in lemmas if l['lemma'] in only_known]
    if min_length > 1:
        lemmas = [l for l in lemmas if len(l['lemma']) >= min_length]
    lemmas = sorted(lemmas, key=lambda x: x[sort], reverse=reverse)
    return lemmas[:num]
```

Remove `from operator import xor` and `from hsg.utils.constants import HEISIG_CSV`
from both files.

In `hsg/commands/frequencytools.py`, update the `freq` command:

```python
# Replace -h/--skip-heisig and -o/--only-heisig with:
@click.option('--skip-known', is_flag=True, default=False, help='Skip known characters.')
@click.option('--only-known', is_flag=True, default=False, help='Show only known characters.')
@click.option('--known-set', type=click.Choice(['heisig', 'hsk', 'file']), default='heisig')
@click.option('--known-file', type=click.Path(exists=True), default=None)
@click.option('--max', 'max_known', type=click.INT, default=-1)

# In the function body:
if skip_known or only_known:
    from hsg.classes.knownset_factory import create_known_set
    ks = create_known_set(known_set, max=max_known, filepath=known_file)
    known_chars = set(ks.get_known_characters())
else:
    known_chars = None

lemmas = fq.get_most_frequent_lemmas(
    type, max_results, skip_known=known_chars, only_known=known_chars if only_known else None,
    min_length=min_length, sort=sort, reverse=reverse,
)
```

- [ ] **Step 4: Run tests + lint + commit**

```bash
pytest tests/ -q
ruff check --fix . && ruff format . && mypy --strict hsg
git add -A
git commit -m "refactor(frequency): rename skip_heisig/only_heisig to skip_known/only_known

- Replace boolean skip_heisig/only_heisig with set[str]|None skip_known/only_known
- Remove direct HEISIG_CSV imports from frequency backends
- Remove xor logic
- Update freq command with --skip-known/--only-known flags"
```

---

## 9. Pluggable story source

### 9.1 Create `hsg/classes/stories.py` — disk-based story store

Stories are stored as JSON: `{"一": {"keyword": "One", "story": "...", ...}, ...}`.
The `stories` command reads from this file instead of querying AnkiConnect.

**Files:**
- Create: `hsg/classes/stories.py`
- Test: `tests/unit/test_stories_store.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_stories_store.py
import json
from hsg.classes.stories import StoryStore


class TestStoryStore:
    def test_load_json(self, tmp_path):
        data = {
            "一": {"keyword": "One", "keyword_ita": "Uno", "story": "<b>One</b>"},
            "二": {"keyword": "Two", "keyword_ita": "Due", "story": "Two things"},
        }
        f = tmp_path / 'stories.json'
        f.write_text(json.dumps(data))

        store = StoryStore(str(f))
        assert store.get_story('一') is not None
        assert store.get_story('一')['keyword'] == 'One'
        assert store.get_story('三') is None

    def test_strip_html(self, tmp_path):
        data = {"一": {"keyword": "One", "story": "<b>One</b>"}}
        f = tmp_path / 'stories.json'
        f.write_text(json.dumps(data))

        store = StoryStore(str(f))
        story = store.get_story('一')
        assert '<b>' not in story['story']
        assert 'One' in story['story']
```

- [ ] **Step 2: Run to verify fail, then implement**

```python
# hsg/classes/stories.py
import json
from html.parser import HTMLParser
from io import StringIO
from typing import Any


class _MLStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text = StringIO()

    def handle_data(self, d: str) -> None:
        self.text.write(d)

    def get_data(self) -> str:
        return self.text.getvalue()


def _strip_tags(html: str) -> str:
    s = _MLStripper()
    s.feed(html)
    return s.get_data()


class StoryStore:
    """Disk-based story store. Reads stories from a JSON file.

    JSON format: {"<hanzi>": {"keyword": str, "keyword_ita": str, "story": str, ...}}
    """

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self._data: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        with open(self.filepath) as f:
            self._data = json.load(f)

    def get_story(self, hanzi: str) -> dict[str, Any] | None:
        entry = self._data.get(hanzi)
        if entry is None:
            return None
        story = dict(entry)
        if 'story' in story:
            story['story'] = _strip_tags(story['story'])
        return story
```

- [ ] **Step 3: Run tests + lint + commit**

```bash
pytest tests/unit/test_stories_store.py -v
ruff check --fix . && ruff format . && mypy --strict hsg
git add hsg/classes/stories.py tests/unit/test_stories_store.py
git commit -m "feat(stories): add disk-based StoryStore"
```

### 9.2 Add `hsg stories import` subcommand

A one-shot importer that queries AnkiConnect and writes stories.json.
This is the old `stories` command logic, repurposed as an importer.

**Files:**
- Modify: `hsg/commands/heisigtools.py` (add `stories_import` command)
- Modify: `hsg/cli.py` (register new command)
- Test: `tests/commands/test_stories.py`

- [ ] **Step 1: Add test for import (mocked)**

```python
# Append to tests/commands/test_stories.py

def test_stories_import(tmp_path, runner, app, monkeypatch):
    """stories import should write a JSON file from AnkiConnect data."""
    output_file = tmp_path / 'stories.json'

    # Mock requests.request to return canned AnkiConnect responses
    import hsg.commands.heisigtools as ht_mod

    class FakeResponse:
        def __init__(self, data: str):
            self.text = data

    call_count = [0]

    def fake_request(method, url, json=None, timeout=None, **kw):
        call_count[0] += 1
        if json and json.get('action') == 'findNotes':
            return FakeResponse('{"result": [1, 2], "error": null}')
        elif json and json.get('action') == 'notesInfo':
            return FakeResponse(
                '{"result": [{"fields": {"Keyword": {"value": "One"}, '
                '"KeywordIta": {"value": "Uno"}, "PrimitiveMeaning": {"value": ""}, '
                '"PrimitiveMeaningIta": {"value": ""}, "Story": {"value": "<b>One</b>"}}}], '
                '"error": null}'
            )
        return FakeResponse('{"result": [], "error": null}')

    monkeypatch.setattr(ht_mod.requests, 'request', fake_request)
    monkeypatch.setattr(ht_mod.requests, 'RequestException', Exception)

    result = runner.invoke(app, ['stories', 'import', '一', '--out', str(output_file)])
    assert result.exit_code == 0
    import json
    data = json.loads(output_file.read_text())
    assert '一' in data
    assert data['一']['keyword'] == 'One'
```

- [ ] **Step 2: Run to verify fail, then implement**

In `hsg/commands/heisigtools.py`, restructure the `stories` command:

1. Rename the existing `stories` command to `stories_import` with
   `@click.command(name='import')` — but `import` is a Python keyword, so
   use a group instead. Better: make `stories` a `click.Group` with
   subcommands `show` (default) and `import`.

Actually, simpler approach that avoids breaking the existing `stories text`
invocation: keep `stories` as the disk-based reader (no Anki), and add a
separate `hsg stories-import` command (flat, not a subgroup).

```python
# Keep stories as disk-based:
@click.command()
@click.argument('text', required=False)
@click.option('-f', '--file', type=click.File('r'), default=sys.stdin)
@click.option('--stories-file', type=click.Path(exists=True), default=None,
              help='Path to stories JSON file.')
def stories(text, file, stories_file):
    """Parses a text and returns Heisig stories from a JSON file."""
    from hsg.classes.stories import StoryStore

    if not stories_file:
        raise click.UsageError('--stories-file is required (use `hsg stories-import` to create one)')

    store = StoryStore(stories_file)
    input_text = get_input(text, file)
    chars = list(input_text.replace('\r', '').replace('\n', '').strip())
    for idx, char in enumerate(chars):
        data = store.get_story(char)
        if not data:
            print(f'{char}: NO STORY')
        else:
            print(f'{char} ({data.get("keyword", "")} | {data.get("keyword_ita", "")}): {data.get("story", "")}')
        if idx < len(chars) - 1:
            print()


# New import command:
@click.command(name='stories-import')
@click.argument('text', required=False)
@click.option('-f', '--file', type=click.File('r'), default=sys.stdin)
@click.option('--out', type=click.Path(), default='stories.json',
              help='Output JSON file (default: stories.json).')
@click.option('--deck', default='Cinese::Heisig', help='Anki deck name.')
def stories_import(text, file, out, deck):
    """Imports stories from AnkiConnect into a JSON file."""
    # ... (the old find_notes/get_note/get_data logic, but writes to --out)
```

In `hsg/cli.py`, add:
```python
from hsg.commands.heisigtools import stories_import
cli.add_command(stories_import)
```

- [ ] **Step 3: Update existing stories test**

The existing `test_stories.py::test_stories_no_anki` test calls
`runner.invoke(app, ['stories', '一'])` — this will now fail because
`--stories-file` is required. Update the test:

```python
def test_stories_no_file(self, patched_constants, runner, app):
    result = runner.invoke(app, ['stories', '一'])
    assert result.exit_code != 0  # UsageError: --stories-file required
```

- [ ] **Step 4: Run tests + lint + commit**

```bash
pytest tests/commands/test_stories.py -v
ruff check --fix . && ruff format . && mypy --strict hsg
git add hsg/commands/heisigtools.py hsg/cli.py tests/commands/test_stories.py
git commit -m "feat(stories): disk-based story source + Anki importer command

- stories command reads from JSON file (--stories-file)
- stories-import command queries AnkiConnect and writes JSON (--out)
- stories-import --deck configurable (default Cinese::Heisig)
- Removes AnkiConnect as a runtime dependency for stories"
```

---

## 10. SentenceCorpus interface

### 10.1 Create `hsg/classes/sentencecorpus.py` — ABC

Decouples sentence loading from known-set filtering. `TatoebaHeisig`
becomes a thin orchestrator that takes a `SentenceCorpus` + `KnownSet`.

**Files:**
- Create: `hsg/classes/sentencecorpus.py`
- Test: `tests/unit/test_sentencecorpus.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_sentencecorpus.py
from hsg.classes.sentencecorpus import SentenceCorpus


class DummyCorpus(SentenceCorpus):
    def __init__(self):
        self._data = {"一二三": ["one two three"], "十": ["ten"]}

    def load(self) -> dict[str, list[str]]:
        return self._data

    def find_sentences(self, keyword: str) -> list[dict]:
        return [{'hanzi': k, 'translations': v} for k, v in self._data.items() if keyword in k]


class TestSentenceCorpus:
    def test_find_sentences(self):
        c = DummyCorpus()
        results = c.find_sentences('一')
        assert len(results) == 1
        assert results[0]['hanzi'] == '一二三'

    def test_find_sentences_no_match(self):
        c = DummyCorpus()
        results = c.find_sentences('九')
        assert len(results) == 0
```

- [ ] **Step 2: Run to verify fail, then implement**

```python
# hsg/classes/sentencecorpus.py
from abc import ABCMeta, abstractmethod
from typing import Any


class SentenceCorpus(metaclass=ABCMeta):
    """ABC for sentence corpora (Tatoeba, CC-CEDICT examples, etc.)."""

    @abstractmethod
    def load(self) -> dict[str, list[str]]:
        """Load sentences into a {hanzi: [translations]} dict."""
        raise NotImplementedError

    def find_sentences(
        self, keyword: str, known_chars: set[str] | None = None,
        max_sentences: int = 10000, reverse: bool = False,
    ) -> list[dict[str, Any]]:
        """Find sentences containing keyword, optionally filtered by known set."""
        data = self.load()
        sentences = []
        for hanzi, translations in data.items():
            if keyword not in hanzi:
                continue
            if known_chars is not None:
                if not all(c in known_chars for c in hanzi):
                    continue
            sentences.append({'hanzi': hanzi, 'translations': translations})
        sentences.sort(key=lambda x: len(x['hanzi']), reverse=reverse)
        return sentences[:max_sentences]

    def find_random_sentences(
        self, number: int, min_length: int = 10, known_chars: set[str] | None = None,
        reverse: bool = False,
    ) -> list[dict[str, Any]]:
        """Find random sentences of minimum length, optionally filtered."""
        import random as _random

        data = self.load()
        candidates = []
        for hanzi, translations in data.items():
            if len(hanzi) < min_length:
                continue
            if known_chars is not None:
                if not all(c in known_chars for c in hanzi):
                    continue
            candidates.append({'hanzi': hanzi, 'translations': translations})
        if len(candidates) < number:
            number = len(candidates)
        sampled = _random.sample(candidates, number)
        sampled.sort(key=lambda x: len(x['hanzi']), reverse=reverse)
        return sampled
```

- [ ] **Step 3: Run tests + lint + commit**

```bash
pytest tests/unit/test_sentencecorpus.py -v
ruff check --fix . && ruff format . && mypy --strict hsg
git add hsg/classes/sentencecorpus.py tests/unit/test_sentencecorpus.py
git commit -m "feat(sentencecorpus): add SentenceCorpus ABC"
```

### 10.2 Create `hsg/classes/tatoeba_corpus.py` — Tatoeba backend

Extracts the TSV loading from `TatoebaHeisig` into a `SentenceCorpus`
implementation. `TatoebaHeisig` is simplified to use this + a `KnownSet`.

**Files:**
- Create: `hsg/classes/tatoeba_corpus.py`
- Test: `tests/unit/test_tatoeba_corpus.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_tatoeba_corpus.py
from hsg.classes.tatoeba_corpus import TatoebaCorpus


class TestTatoebaCorpus:
    def test_load(self, patched_constants):
        from hsg.utils.constants import TATOEBA_CSV
        c = TatoebaCorpus(TATOEBA_CSV)
        data = c.load()
        assert '一二三' in data
        assert len(data['一二三']) >= 1

    def test_find_sentences(self, patched_constants):
        from hsg.utils.constants import TATOEBA_CSV
        c = TatoebaCorpus(TATOEBA_CSV)
        results = c.find_sentences('一')
        assert len(results) > 0
        assert '一' in results[0]['hanzi']
```

- [ ] **Step 2: Run to verify fail, then implement**

```python
# hsg/classes/tatoeba_corpus.py
import csv
from typing import Any

from hsg.classes.sentencecorpus import SentenceCorpus


class TatoebaCorpus(SentenceCorpus):
    """SentenceCorpus backed by Tatoeba TSV."""

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self._data: dict[str, list[str]] | None = None

    def load(self) -> dict[str, list[str]]:
        if self._data is not None:
            return self._data
        self._data = {}
        with open(self.filepath) as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if len(row) < 4:
                    continue
                hanzi = row[1]
                english = row[3]
                if hanzi not in self._data:
                    self._data[hanzi] = [english]
                else:
                    self._data[hanzi].append(english)
        return self._data
```

- [ ] **Step 3: Run tests + lint + commit**

```bash
pytest tests/unit/test_tatoeba_corpus.py -v
ruff check --fix . && ruff format . && mypy --strict hsg
git add hsg/classes/tatoeba_corpus.py tests/unit/test_tatoeba_corpus.py
git commit -m "feat(tatoeba): extract TatoebaCorpus from TatoebaHeisig"
```

### 10.3 Refactor `sentences`/`random` commands to use SentenceCorpus + KnownSet

Replace `TatoebaHeisig` with direct use of `TatoebaCorpus` + `KnownSet`.

**Files:**
- Modify: `hsg/commands/heisigtatoeba.py`
- Modify: `tests/commands/test_sentences.py`
- Modify: `tests/commands/test_random.py`

- [ ] **Step 1: Update the commands**

Replace the `TatoebaHeisig` usage in `sentences` and `random`:

```python
from hsg.classes.tatoeba_corpus import TatoebaCorpus
from hsg.classes.knownset_factory import create_known_set

# In sentences command:
if all_characters:
    known_chars = None  # no filtering
else:
    ks_backend = known_set or 'heisig'
    ks_max = max_known if max_known is not None else max_frame
    if ks_backend == 'file':
        ks = create_known_set('file', filepath=known_file)
    else:
        ks = create_known_set(ks_backend, max=ks_max, frequencies_corpus='subtlexch')
    known_chars = set(ks.get_known_characters())

corpus = TatoebaCorpus(TATOEBA_CSV)
found = corpus.find_sentences(keyword, known_chars=known_chars, max_sentences=max_sentences, reverse=reverse)
# print_sentences stays the same, just move it to a standalone function
```

Remove `TatoebaHeisig` class entirely. Move `print_sentences` to a
standalone function in `heisigtatoeba.py` (it doesn't need `self`).

- [ ] **Step 2: Update tests**

Existing tests should pass with the same CLI invocations. Add a test for
`--known-set file`:

```python
def test_sentences_known_set_file(patched_constants, runner, app, tmp_path):
    known_file = tmp_path / 'known.txt'
    known_file.write_text('一\n二\n三\n')
    result = runner.invoke(app, ['sentences', '一', '--known-set', 'file',
                                  '--known-file', str(known_file), '-f', 'json'])
    assert result.exit_code == 0
    data = json.loads(result.output.strip(), strict=False)
    # Only sentences where ALL chars are in {一,二,三} + ADDITIONAL
    for s in data:
        assert all(c in '一二三' or c in '!?,. ' for c in s['hanzi'])
```

- [ ] **Step 3: Run tests + lint + commit**

```bash
pytest tests/ -q
ruff check --fix . && ruff format . && mypy --strict hsg
git add hsg/commands/heisigtatoeba.py tests/commands/test_sentences.py tests/commands/test_random.py
git commit -m "refactor(sentences): replace TatoebaHeisig with TatoebaCorpus + KnownSet

- Remove TatoebaHeisig class (duplicate Heisig parser eliminated)
- sentences/random commands use TatoebaCorpus.find_sentences(known_chars=...)
- print_sentences extracted as standalone function"
```

---

## 11. Centralise Frequency factory

### 11.1 Create `hsg/classes/frequency_factory.py`

Remove the 3 duplicated `{'renminwang': ..., 'subtlexch': ...}[corpus]()`
dispatches.

**Files:**
- Create: `hsg/classes/frequency_factory.py`
- Modify: `hsg/classes/heisig.py` (replace inline dispatch)
- Modify: `hsg/classes/ccedict.py` (replace inline dispatch)
- Modify: `hsg/commands/frequencytools.py` (replace inline dispatch)
- Test: `tests/unit/test_frequency_factory.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_frequency_factory.py
from hsg.classes.frequency import Frequency
from hsg.classes.frequency_factory import create_frequency


class TestFrequencyFactory:
    def test_create_subtlexch(self, patched_constants):
        fq = create_frequency('subtlexch')
        assert isinstance(fq, Frequency)
        assert fq.find_char('一') is not None

    def test_create_renminwang(self, patched_constants):
        fq = create_frequency('renminwang')
        assert isinstance(fq, Frequency)
        assert fq.find_char('一') is not None

    def test_invalid(self):
        import pytest
        with pytest.raises(ValueError):
            create_frequency('bad-corpus')
```

- [ ] **Step 2: Run to verify fail, then implement**

```python
# hsg/classes/frequency_factory.py
from hsg.classes.frequency import Frequency


def create_frequency(corpus: str) -> Frequency:
    """Create a Frequency instance by corpus name."""
    if corpus == 'renminwang':
        from hsg.classes.renminwang import RenMinWang
        return RenMinWang()
    if corpus == 'subtlexch':
        from hsg.classes.subtlexch import SubtlexCh
        return SubtlexCh()
    raise ValueError(f'unknown frequency corpus: {corpus}')
```

Then replace the inline dispatches in `heisig.py:17`, `ccedict.py:33`,
`frequencytools.py:72` with `create_frequency(corpus)`.

- [ ] **Step 3: Run tests + lint + commit**

```bash
pytest tests/ -q
ruff check --fix . && ruff format . && mypy --strict hsg
git add hsg/classes/frequency_factory.py hsg/classes/heisig.py hsg/classes/ccedict.py hsg/commands/frequencytools.py tests/unit/test_frequency_factory.py
git commit -m "refactor(frequency): centralise frequency factory, remove 3 dispatch duplications"
```

---

## 12. Update conftest and final verification

### 12.1 Update `tests/conftest.py`

Add any new path constants needed by the new modules to the
`patched_constants` fixture. Specifically:
- `hsg.classes.tatoeba_corpus` imports `TATOEBA_CSV` — already patched.
- No new path constants are introduced (file knownset takes a user path,
  stories store takes a user path).

Verify the full suite passes with the updated fixtures.

### 12.2 Final verification

Run the complete acceptance check:

```bash
ruff check .
ruff format --check .
mypy --strict hsg
pre-commit run --all-files
pytest --cov=hsg --cov-report=term-missing --cov-fail-under=70
```

Smoke test the new CLI:

```bash
# Existing workflows still work
hsg parse "你好世界" -t json | python -m json.tool >/dev/null && echo "parse json OK"
hsg enrich "一二三" -m 5
hsg list --min 1 --max 3 -f json
hsg sentences "一" -m 5 -f json
hsg freq "一" -m 5 -t json

# New known-set workflows
hsg parse "你好" --known-set hsk --max 2 -t json
hsg parse "你好" --known-set file --known-file known.txt -t json
hsg enrich "一二三" --known-set hsk --max 1
hsg sentences "一" --known-set hsk --max 2 -f json
hsg freq "一" --skip-known -t json

# Stories import + show (mocked)
hsg stories-import "一" --out /tmp/stories.json
hsg stories "一" --stories-file /tmp/stories.json
```

---

## 13. Commit plan

| # | Commit message | Task |
|---|---|---|
| 1 | `refactor(knownset): add KnownSet ABC, make Heisig implement it` | §1+§2 |
| 2 | `feat(knownset): add HSK KnownSet backend` | §3 |
| 3 | `feat(knownset): add file-based KnownSet backend` | §4 |
| 4 | `feat(knownset): add factory for KnownSet backends` | §5 |
| 5 | `feat(parse): add --known-set option for pluggable backends` | §6.1 |
| 6 | `feat(enrich): add --known-set option for pluggable backends` | §6.2 |
| 7 | `refactor(sentences): decouple TatoebaHeisig from Heisig, use KnownSet` | §7 |
| 8 | `refactor(frequency): rename skip_heisig/only_heisig to skip_known/only_known` | §8 |
| 9 | `feat(stories): disk-based StoryStore` | §9.1 |
| 10 | `feat(stories): Anki importer + disk-based stories command` | §9.2 |
| 11 | `feat(sentencecorpus): add SentenceCorpus ABC` | §10.1 |
| 12 | `feat(tatoeba): extract TatoebaCorpus from TatoebaHeisig` | §10.2 |
| 13 | `refactor(sentences): replace TatoebaHeisig with TatoebaCorpus + KnownSet` | §10.3 |
| 14 | `refactor(frequency): centralise frequency factory` | §11 |

Commits 1-4 are foundational (ABC + backends). 5-7 refactor commands.
8 cleans up the Frequency ABC. 9-10 restructure stories. 11-13 restructure
sentences. 14 is cleanup.

---

## 14. Acceptance criteria

- [ ] `KnownSet` ABC in `hsg/classes/knownset.py` with `is_known`,
      `get_known_characters`, `is_additional_character`, `get_char_info`,
      `get_statistics`.
- [ ] `Heisig` implements `KnownSet`; `get_statistics` inherited, not
      duplicated.
- [ ] `HSKKnownSet` backend: `--known-set hsk --max 3` works for
      `parse`, `enrich`, `sentences`, `random`.
- [ ] `FileKnownSet` backend: `--known-set file --known-file known.txt`
      works for `parse`, `enrich`, `sentences`, `random`.
- [ ] `KnownSet` factory in `hsg/classes/knownset_factory.py`.
- [ ] `--max-frame` kept as deprecated alias on `parse`, `enrich`,
      `sentences`, `random` (maps to `--known-set heisig --max <value>`).
- [ ] `Frequency.get_most_frequent_lemmas` uses `skip_known`/`only_known`
      (set[str] | None), not `skip_heisig`/`only_heisig` (bool).
- [ ] `RenMinWang` and `SubtlexCh` no longer import `HEISIG_CSV`.
- [ ] `hsg stories` reads from a JSON file (`--stories-file`); no
      AnkiConnect dependency at runtime.
- [ ] `hsg stories-import` queries AnkiConnect and writes JSON.
- [ ] `SentenceCorpus` ABC in `hsg/classes/sentencecorpus.py`.
- [ ] `TatoebaCorpus` implements `SentenceCorpus`.
- [ ] `TatoebaHeisig` class removed (no duplicate Heisig TSV parser).
- [ ] Frequency factory in `hsg/classes/frequency_factory.py`; no inline
      dispatch in `heisig.py`, `ccedict.py`, `frequencytools.py`.
- [ ] `ruff check .`, `ruff format --check .`, `mypy --strict hsg`,
      `pytest --cov-fail-under=70` all green.
- [ ] A learner who has never touched Heisig can run:
      `hsg parse "你好" --known-set hsk --max 2 -t json` and get
      meaningful coverage output.

---

## 15. Out of scope for Phase 2

- Anki-export KnownSet backend (parsing `.apkg` files) — deferred to Phase 5;
  the file backend covers the "user-supplied list" use case for now.
- Pleco-flashcards KnownSet backend — Phase 5.
- CC-CEDICT examples as a second SentenceCorpus — Phase 5.
- Renaming the package or repo — Phase 3.
- README / docs / LICENSE — Phase 3.
- Removing `--max-frame` entirely — future phase after deprecation period.
- Replacing `dict[str, Any]` with dataclasses (`Lemma`, `Frame`, `Sentence`)
  — the type aliases can be introduced but full dataclass migration is
  Phase 2.5 or Phase 5.
- `tatoebasqlite.py` resurrection (SQLite backend for Tatoeba) — the
  `SentenceCorpus` ABC is in place, but the SQLite adapter itself is
  deferred; the TSV-based `TatoebaCorpus` is sufficient.
