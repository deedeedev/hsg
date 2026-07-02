import csv
import json
import sys
from typing import Any

import click
from rich import print
from tabulate import tabulate

from hsg.classes.frequency import Frequency
from hsg.classes.frequency_factory import create_frequency
from hsg.classes.knownset_factory import create_known_set
from hsg.utils.io import get_input


@click.command(name='freq')
@click.argument('text', required=False)
@click.option('-f', '--file', type=click.File('r'), default=sys.stdin)
@click.option('-k', '--skip-clipboard', required=False, is_flag=True, help='Skip clipboard content.')
@click.option(
    '-m', '--max-results', required=False, type=click.INT, default=-1, help='Show max n results (default all).'
)
@click.option('--skip-known', is_flag=True, default=False, help='Skip known characters.')
@click.option('--only-known', is_flag=True, default=False, help='Show only known characters.')
@click.option(
    '--known-set',
    type=click.Choice(['heisig', 'hsk', 'file']),
    default='heisig',
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
    default=-1,
    help='Max frame/level for known-set.',
)
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
    skip_known: bool,
    only_known: bool,
    known_set: str,
    known_file: str | None,
    max_known: int,
    type: str,
    min_length: int,
    sort: str,
    reverse: bool,
    frequencies_corpus: str,
    format: str,
) -> None:
    fq: Frequency = create_frequency(frequencies_corpus)

    if skip_known or only_known:
        if known_set == 'file':
            if not known_file:
                raise click.UsageError('--known-set file requires --known-file')
            ks = create_known_set('file', filepath=known_file)
        else:
            ks = create_known_set(known_set, max=max_known)
        known_chars: set[str] | None = set(ks.get_known_characters())
    else:
        known_chars = None

    skip_chars = known_chars if skip_known else None
    only_chars = known_chars if only_known else None

    lemmas = fq.get_most_frequent_lemmas(
        type,
        max_results,
        skip_known=skip_chars,
        only_known=only_chars,
        min_length=min_length,
        sort=sort,
        reverse=reverse,
    )

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
