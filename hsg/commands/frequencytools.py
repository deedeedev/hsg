import sys
import csv
import json
import click
import clipboard

from tabulate import tabulate
from hsg.classes.heisig import Heisig
from hsg.classes.renminwang import RenMinWang
from hsg.classes.subtlexch import SubtlexCh


@click.command()
@click.argument('text', required=False)
@click.option('-f', '--file', type=click.File('r'), default=sys.stdin)
@click.option('-k', '--skip-clipboard', required=False, is_flag=True, help='Skip clipboard content.')
@click.option('-m', '--max-results', required=False, type=click.INT, default=-1, help='Show max n results (default all).')
@click.option('-h', '--skip-heisig', required=False, is_flag=True, default=False, help='Skip Heisig characters.')
@click.option('-o', '--only-heisig', required=False, is_flag=True, default=False, help='Show only Heisig characters.')
@click.option('-p', '--type', type=click.Choice(['chars', 'words']), default='chars', help='Return character or word frequencies (default chars).')
@click.option('-l', '--min_length', type=click.INT, default=1, help='Minimum word length.')
@click.option('-s', '--sort', type=click.Choice(['count', 'count_million', 'count_log', 'cd', 'cd_percent', 'cd_log', 'rank', 'count_x_cd']), default='rank', help='Sort results specified field.')
@click.option('-r', '--reverse', required=False, is_flag=True, default=False, help='Reverse order if sorting by hsk or frequency.')
@click.option('-c', '--frequencies-corpus', type=click.Choice(['renminwang', 'subtlexch']), default='subtlexch', help='Frequencies data corpus.')
@click.option('-t', '--format', required=False, type=click.Choice(['csv', 'json', 'tabulate']), default='tabulate', help='Output format (default tabulate).')
def search(text, file, skip_clipboard, max_results, skip_heisig, only_heisig, type, min_length, sort, reverse, frequencies_corpus, format):
    fq = {'renminwang': RenMinWang, 'subtlexch': SubtlexCh}[frequencies_corpus]()
    lemmas = fq.get_most_frequent_lemmas(type, max_results, skip_heisig, only_heisig, min_length, sort, reverse)

    # filter results by text input
    input = get_input(text, file)
    if input and not skip_clipboard:
        chars = [c for c in input.replace('\r', '').replace('\n', '').strip()]
        lemmas = [l for l in lemmas if l['lemma'] in chars]

    if lemmas:
        if format == 'csv':
            writer = csv.DictWriter(sys.stdout, fieldnames=list(lemmas[0].keys()), delimiter='\t', extrasaction='ignore')
            writer.writeheader()
            writer.writerows(lemmas)
        elif format == 'json':
            print(json.dumps(lemmas))
        elif format == 'tabulate':
            print(tabulate(lemmas, headers='keys', tablefmt='github'))


def get_input(text, file):
    """
    Gets input from argument, then stdin, then clipboard
    """
    if text:
        # text argument
        return text
    elif file and not sys.stdin.isatty():
        with file:
            # 1st fallback: stdin
            return file.read()
    else:
        # 2nd fallback: clipboard
        return clipboard.paste()


if __name__ == '__main__':
    search()
