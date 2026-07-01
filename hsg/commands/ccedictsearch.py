import click

from hsg.classes.ccedict import Ccedict
from hsg.utils.constants import CCEDICT_CSV


@click.command(name='lookup')
@click.argument('query')
@click.option('-e', '--exact', required=False, is_flag=True, default=False, help='Search exact expression.')
@click.option(
    '-t', '--show-traditional', required=False, is_flag=True, default=False, help='Show traditional characters.'
)
@click.option(
    '-f',
    '--format',
    required=False,
    type=click.Choice(['csv', 'json', 'tabulate']),
    default='tabulate',
    help='Output format (default csv).',
)
@click.option(
    '-s',
    '--sort',
    type=click.Choice(['hsk', 'frequency']),
    default='frequency',
    help='Sort results by hsk or frequency.',
)
@click.option(
    '-c',
    '--frequencies-corpus',
    type=click.Choice(['renminwang', 'subtlexch']),
    default='subtlexch',
    help='Frequencies data corpus.',
)
@click.option(
    '-r', '--reverse', required=False, is_flag=True, default=False, help='Reverse order if sorting by hsk or frequency.'
)
@click.option(
    '-h',
    '--max-hsk',
    required=False,
    type=click.Choice(['1', '2', '3', '4', '5', '6', '7', '7-9']),
    default=None,
    help='Show only words with specified hsk level or above.',
)
@click.option(
    '-m', '--max-results', required=False, type=click.INT, default=15, help='Show max n results (default 15).'
)
@click.option('-a', '--all-results', required=False, is_flag=True, default=False, help='Show all results.')
def search(
    query: str,
    exact: bool,
    show_traditional: bool,
    format: str,
    sort: str,
    frequencies_corpus: str,
    reverse: bool,
    max_hsk: str,
    max_results: int,
    all_results: bool,
) -> None:
    ce: Ccedict = Ccedict(CCEDICT_CSV, frequencies_corpus)
    ce.search(query, exact, show_traditional, format, sort, reverse, max_hsk, max_results, all_results)
