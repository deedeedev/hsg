import csv
import json
import sys

import click
from pypinyin import pinyin
from rich import print
from tabulate import tabulate

from hsg.classes.knownset_factory import create_known_set
from hsg.classes.tatoeba_corpus import TatoebaCorpus
from hsg.utils.constants import TATOEBA_CSV

Sentence = dict[str, str | list[str]]


def print_sentences(sentences: list[Sentence], format: str) -> None:
    for s in sentences:
        s['pinyin'] = ' '.join([p[0] for p in pinyin(s['hanzi'])])
    if format == 'csv':
        writer = csv.writer(sys.stdout, delimiter='\t')
        for s in sentences:
            writer.writerow([s['hanzi'], s['pinyin'], ' / '.join(s['translations'])])
    elif format == 'json':
        print(json.dumps(sentences))
    elif format == 'tabulate':
        for s in sentences:
            s['translations'] = ' / '.join(s['translations'])
        print(tabulate(sentences, headers='keys', tablefmt='github'))


def _resolve_known_chars(
    all_characters: bool,
    known_set: str | None,
    known_file: str | None,
    max_known: int | None,
    max_frame: int,
) -> set[str] | None:
    """Resolve the known-chars set, or None for no filtering."""
    if all_characters:
        return None
    ks_backend = known_set or 'heisig'
    ks_max = max_known if max_known is not None else max_frame
    if ks_backend == 'file':
        if not known_file:
            raise click.UsageError('--known-set file requires --known-file')
        ks = create_known_set('file', filepath=known_file)
    else:
        ks = create_known_set(ks_backend, max=ks_max, frequencies_corpus='subtlexch')
    return set(ks.get_known_characters())


@click.command()
@click.argument('keyword')
@click.option('-m', '--max-frame', type=click.INT, default=-1, help='Max Heisig frame known. (default MAX)')
@click.option(
    '-a', '--all-characters', required=False, is_flag=True, default=False, help='Allow all non-Heisig characters.'
)
@click.option('-n', '--max-sentences', type=click.INT, default=10000, help='Max sentences to return (default ALL)')
@click.option(
    '-r', '--reverse', required=False, is_flag=True, default=False, help='Return longer sentences first (default FALSE)'
)
@click.option(
    '-f', '--format', type=click.Choice(['csv', 'json', 'tabulate']), default='csv', help='Output format (default csv).'
)
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
def sentences(
    keyword: str,
    max_frame: int,
    all_characters: bool,
    max_sentences: int,
    reverse: bool,
    format: str,
    known_set: str | None,
    known_file: str | None,
    max_known: int | None,
) -> None:
    """Returns all sentences from the Tatoeba corpus with the specified keyword"""
    known_chars = _resolve_known_chars(all_characters, known_set, known_file, max_known, max_frame)
    corpus = TatoebaCorpus(TATOEBA_CSV)
    found = corpus.find_sentences(keyword, known_chars=known_chars, max_sentences=max_sentences, reverse=reverse)
    print_sentences(found, format)


@click.command(name='random')
@click.option('-m', '--max-frame', type=click.INT, default=-1, help='Max Heisig frame known.')
@click.option(
    '-a', '--all-characters', required=False, is_flag=True, default=False, help='Allow all non-Heisig characters.'
)
@click.option('-n', '--sentences-number', type=click.INT, default=10, help='Return n sentences (default 10).')
@click.option(
    '-l', '--min-length', type=click.INT, default=10, help='Return only sentences of length l or above (default 10).'
)
@click.option(
    '-r', '--reverse', required=False, is_flag=True, default=False, help='Return longer sentences first (default FALSE)'
)
@click.option(
    '-f', '--format', type=click.Choice(['csv', 'json', 'tabulate']), default='csv', help='Output format (default csv).'
)
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
def random_sentences(
    max_frame: int,
    all_characters: bool,
    sentences_number: int,
    min_length: int,
    reverse: bool,
    format: str,
    known_set: str | None,
    known_file: str | None,
    max_known: int | None,
) -> None:
    """Returns random sentences from the Tatoeba corpus with the specified keyword"""
    known_chars = _resolve_known_chars(all_characters, known_set, known_file, max_known, max_frame)
    corpus = TatoebaCorpus(TATOEBA_CSV)
    found = corpus.find_random_sentences(
        sentences_number, min_length=min_length, known_chars=known_chars, reverse=reverse
    )
    print_sentences(found, format)
