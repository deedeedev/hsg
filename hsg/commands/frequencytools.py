import csv
import json
import sys
from typing import Any

import click
from rich import print
from tabulate import tabulate

from hsg.classes.frequency import Frequency
from hsg.classes.renminwang import RenMinWang
from hsg.classes.subtlexch import SubtlexCh
from hsg.utils.io import get_input


@click.command(name='freq')
@click.argument('text', required=False)
@click.option('-f', '--file', type=click.File('r'), default=sys.stdin)
@click.option('-k', '--skip-clipboard', required=False, is_flag=True, help='Skip clipboard content.')
@click.option(
    '-m', '--max-results', required=False, type=click.INT, default=-1, help='Show max n results (default all).'
)
@click.option('-h', '--skip-heisig', required=False, is_flag=True, default=False, help='Skip Heisig characters.')
@click.option('-o', '--only-heisig', required=False, is_flag=True, default=False, help='Show only Heisig characters.')
@click.option(
    '-p',
    '--type',
    type=click.Choice(['chars', 'words']),
    default='chars',
    help='Return character or word frequencies (default chars).',
)
@click.option('-l', '--min_length', type=click.INT, default=1, help='Minimum word length.')
@click.option(
    '-s',
    '--sort',
    type=click.Choice(['count', 'count_million', 'count_log', 'cd', 'cd_percent', 'cd_log', 'rank', 'count_x_cd']),
    default='rank',
    help='Sort results specified field.',
)
@click.option(
    '-r', '--reverse', required=False, is_flag=True, default=False, help='Reverse order if sorting by hsk or frequency.'
)
@click.option(
    '-c',
    '--frequencies-corpus',
    type=click.Choice(['renminwang', 'subtlexch']),
    default='subtlexch',
    help='Frequencies data corpus.',
)
@click.option(
    '-t',
    '--format',
    required=False,
    type=click.Choice(['csv', 'json', 'tabulate']),
    default='tabulate',
    help='Output format (default tabulate).',
)
def search(
    text: str | None,
    file: Any,
    skip_clipboard: bool,
    max_results: int,
    skip_heisig: bool,
    only_heisig: bool,
    type: str,
    min_length: int,
    sort: str,
    reverse: bool,
    frequencies_corpus: str,
    format: str,
) -> None:
    fq: Frequency = {'renminwang': RenMinWang, 'subtlexch': SubtlexCh}[frequencies_corpus]()
    lemmas = fq.get_most_frequent_lemmas(type, max_results, skip_heisig, only_heisig, min_length, sort, reverse)

    # filter results by text input
    input_text = get_input(text, file)
    if input_text and not skip_clipboard:
        chars = list(input_text.replace('\r', '').replace('\n', '').strip())
        lemmas = [lemma for lemma in lemmas if lemma['lemma'] in chars]

    if lemmas:
        if format == 'csv':
            writer: csv.DictWriter[str] = csv.DictWriter(
                sys.stdout, fieldnames=list(lemmas[0].keys()), delimiter='\t', extrasaction='ignore'
            )
            writer.writeheader()
            writer.writerows(lemmas)
        elif format == 'json':
            print(json.dumps(lemmas))
        elif format == 'tabulate':
            print(tabulate(lemmas, headers='keys', tablefmt='github'))
