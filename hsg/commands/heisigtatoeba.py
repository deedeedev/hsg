import csv
import json
import random
import sys

import click
from pypinyin import pinyin
from rich import print
from tabulate import tabulate

from hsg.utils.constants import ADDITIONAL_CHARACTERS, HEISIG_CSV, TATOEBA_CSV

# TODO utilizzare click per l'output colorato al posto di rich (https://click.palletsprojects.com/en/8.0.x/utils/#ansi-colors)


Frame = dict[str, str]
Sentence = dict[str, str | list[str]]


class TatoebaHeisig:
    def __init__(self, tatoebacsv: str, heisigcsv: str, maxframe: int) -> None:
        self.tatoebacsv: str = tatoebacsv
        self.heisigcsv: str = heisigcsv
        self.maxframe: int = maxframe
        self.tatoeba: dict[str, list[str]] = {}
        self.heisig: dict[str, Frame] = {}
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

    def load_heisig(self) -> None:
        with open(self.heisigcsv) as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                frame_number: str = row[2]
                if frame_number.startswith('v') or not frame_number:
                    continue
                hanzi: str = row[0]
                keyword: str = row[4]
                pinyin: str = row[5]
                self.heisig[hanzi] = {
                    'frame': frame_number,
                    'keyword': keyword,
                    'pinyin': pinyin,
                }

    def get_allowed_frames(self) -> list[str]:
        if self.maxframe == -1:
            return list(self.heisig.keys())
        return [hanzi for hanzi in self.heisig if int(self.heisig[hanzi]['frame']) <= self.maxframe]

    def get_allowed_characters(self) -> list[str]:
        return self.get_allowed_frames() + list(ADDITIONAL_CHARACTERS)

    def get_all_allowed_sentences(self) -> None:
        self.load_tatoeba()
        self.load_heisig()
        count = 0
        allowed: list[str] = self.get_allowed_characters()
        for sentence in self.tatoeba:
            if self.maxframe == -1 or all(char in allowed for char in sentence):
                self.allowed_sentences.append({'hanzi': sentence, 'translations': self.tatoeba[sentence]})
                count += 1

    # find all allowed sentences containing keyword
    def find_sentences(self, keyword, max_sentences, reverse):
        if not self.allowed_sentences:
            self.get_all_allowed_sentences()
        sentences = [sentence for sentence in self.allowed_sentences if keyword in sentence['hanzi']]
        # longer sentences first
        return sorted(sentences, key=lambda x: len(x['hanzi']), reverse=reverse)[:max_sentences]

    # get n allowed sentences of length >= minlength
    def find_random_sentences(self, number, minlength, reverse):
        if not self.allowed_sentences:
            self.get_all_allowed_sentences()
        minlength_sentences = [sentence for sentence in self.allowed_sentences if len(sentence['hanzi']) >= minlength]
        minlength_sentences = random.sample(minlength_sentences, number)
        return sorted(minlength_sentences, key=lambda x: len(x['hanzi']), reverse=reverse)

    def print_sentences(self, sentences, format):
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
def sentences(
    keyword: str, max_frame: int, all_characters: bool, max_sentences: int, reverse: bool, format: str
) -> None:
    """
    Returns all sentences from the Tatoeba corpus with the specified keyword

    python heisigtatoeba.py sentences -m 1500 -n 20 "爱"
    """
    if all_characters:
        max_frame = -1
    ht = TatoebaHeisig(TATOEBA_CSV, HEISIG_CSV, max_frame)
    sentences = ht.find_sentences(keyword, max_sentences, reverse)
    ht.print_sentences(sentences, format)


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
def random_sentences(
    max_frame: int, all_characters: bool, sentences_number: int, min_length: int, reverse: bool, format: str
) -> None:
    """
    Returns random sentences from the Tatoeba corpus with the specified keyword

    python heisigtatoeba.py sentences -m 1500 -n 10 -l 10
    """
    if all_characters:
        max_frame = -1
    ht = TatoebaHeisig(TATOEBA_CSV, HEISIG_CSV, max_frame)
    sentences = ht.find_random_sentences(sentences_number, min_length, reverse)
    ht.print_sentences(sentences, format)
