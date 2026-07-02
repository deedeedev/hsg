import csv
import json
import random
import sys

import click
from pypinyin import pinyin
from rich import print
from tabulate import tabulate

from hsg.classes.knownset import KnownSet
from hsg.classes.knownset_factory import create_known_set
from hsg.utils.constants import TATOEBA_CSV

Frame = dict[str, str]
Sentence = dict[str, str | list[str]]


class TatoebaHeisig:
    def __init__(self, tatoebacsv: str, known_set: KnownSet) -> None:
        self.tatoebacsv: str = tatoebacsv
        self.known_set = known_set
        self.tatoeba: dict[str, list[str]] = {}
        self.allowed_sentences: list[Sentence] = []

    def load_tatoeba(self) -> None:
        with open(self.tatoebacsv) as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                hanzi: str = row[1]
                english: str = row[3]
                if hanzi not in self.tatoeba:
                    self.tatoeba[hanzi] = [english]
                else:
                    self.tatoeba[hanzi].append(english)

    def get_allowed_characters(self) -> list[str]:
        return self.known_set.get_known_characters()

    def get_all_allowed_sentences(self) -> None:
        self.load_tatoeba()
        allowed = set(self.get_allowed_characters())
        for sentence in self.tatoeba:
            if all(char in allowed for char in sentence):
                self.allowed_sentences.append({'hanzi': sentence, 'translations': self.tatoeba[sentence]})

    def find_sentences(self, keyword: str, max_sentences: int, reverse: bool) -> list[Sentence]:
        if not self.allowed_sentences:
            self.get_all_allowed_sentences()
        sentences = [sentence for sentence in self.allowed_sentences if keyword in sentence['hanzi']]
        return sorted(sentences, key=lambda x: len(x['hanzi']), reverse=reverse)[:max_sentences]

    def find_random_sentences(self, number: int, minlength: int, reverse: bool) -> list[Sentence]:
        if not self.allowed_sentences:
            self.get_all_allowed_sentences()
        minlength_sentences = [sentence for sentence in self.allowed_sentences if len(sentence['hanzi']) >= minlength]
        minlength_sentences = random.sample(minlength_sentences, number)
        return sorted(minlength_sentences, key=lambda x: len(x['hanzi']), reverse=reverse)

    def print_sentences(self, sentences: list[Sentence], format: str) -> None:
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
    if all_characters:
        ks = create_known_set('heisig', max=-1, frequencies_corpus='subtlexch')
    else:
        ks_backend = known_set or 'heisig'
        ks_max = max_known if max_known is not None else max_frame
        if ks_backend == 'file':
            if not known_file:
                raise click.UsageError('--known-set file requires --known-file')
            ks = create_known_set('file', filepath=known_file)
        else:
            ks = create_known_set(ks_backend, max=ks_max, frequencies_corpus='subtlexch')
    ht = TatoebaHeisig(TATOEBA_CSV, ks)
    found = ht.find_sentences(keyword, max_sentences, reverse)
    ht.print_sentences(found, format)


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
    if all_characters:
        ks = create_known_set('heisig', max=-1, frequencies_corpus='subtlexch')
    else:
        ks_backend = known_set or 'heisig'
        ks_max = max_known if max_known is not None else max_frame
        if ks_backend == 'file':
            if not known_file:
                raise click.UsageError('--known-set file requires --known-file')
            ks = create_known_set('file', filepath=known_file)
        else:
            ks = create_known_set(ks_backend, max=ks_max, frequencies_corpus='subtlexch')
    ht = TatoebaHeisig(TATOEBA_CSV, ks)
    found = ht.find_random_sentences(sentences_number, min_length, reverse)
    ht.print_sentences(found, format)
