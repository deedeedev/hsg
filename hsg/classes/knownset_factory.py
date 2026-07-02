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
