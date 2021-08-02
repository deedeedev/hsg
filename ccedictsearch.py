import click

from classes.ccedict import Ccedict
from utils.constants import CCEDICT_CSV


@click.command()
@click.argument('query')
@click.option('-e', '--exact', required=False, is_flag=True, default=False, help='Search exact expression.')
@click.option('-t', '--show-traditional', required=False, is_flag=True, default=False, help='Show traditional characters.')
@click.option('-f', '--format', required=False, type=click.Choice(['csv', 'json', 'tabulate']), default='tabulate', help='Output format (default csv).')
@click.option('-m', '--max-results', required=False, type=click.INT, default=15, help='Show max n results (default 15).')
@click.option('-a', '--all-results', required=False, is_flag=True, default=False, help='Show all results.')
def search(query: str, exact: bool, show_traditional: bool, format: str, max_results: int, all_results: bool):
    ce: Ccedict = Ccedict(CCEDICT_CSV)
    ce.search(query, exact, show_traditional, format, max_results, all_results)


if __name__ == '__main__':
    search()
