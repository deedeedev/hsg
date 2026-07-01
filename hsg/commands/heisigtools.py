import sys
import json
import requests
from io import StringIO
from html.parser import HTMLParser

import click
from rich import print
from pypinyin import pinyin, lazy_pinyin, Style

from hsg.classes.heisig import Heisig
from hsg.classes.hsk import HSK
from hsg.utils.io import get_input
from hsg.utils.writers import WRITERS, validate_fields


@click.command()
@click.argument('text', required=False)
@click.option('-f', '--file', type=click.File('r'), default=sys.stdin)
def stories(text, file):
    """
    Parses a text and returns a list of Heisig stories.
    If no text is passed as argument fallbacks to stdin then clipboard
    """

    def find_notes(hanzi):
        url = "http://localhost:8765"
        payload = {
            "action": "findNotes",
            "version": 6,
            "params": {
                "query": f"deck:Cinese::Heisig Hanzi:{hanzi}",
            }
        }
        response = requests.request("POST", url, json=payload)
        ids = json.loads(response.text)["result"]
        return ids

    def get_note(id):
        url = "http://localhost:8765"
        payload = {
            "action": "notesInfo",
            "version": 6,
            "params": {
                "notes": [id],
            }
        }
        response = requests.request("POST", url, json=payload)
        notes = json.loads(response.text)["result"]
        if len(notes) > 0:
            return notes[0]
        return None

    def get_data(hanzi):
        ids = find_notes(hanzi)
        if ids:
            note = get_note(ids[0])
            if note:
                return {
                    "keyword": note['fields']['Keyword']['value'],
                    "keyword_ita": note['fields']['KeywordIta']['value'],
                    "primitive": note['fields']['PrimitiveMeaning']['value'],
                    "primitive_ita": note['fields']['PrimitiveMeaningIta']['value'],
                    "story": note['fields']['Story']['value'],
                }
        return None

    class MLStripper(HTMLParser):
        def __init__(self):
            super().__init__()
            self.reset()
            self.strict = False
            self.convert_charrefs = True
            self.text = StringIO()

        def handle_data(self, d):
            self.text.write(d)

        def get_data(self):
            return self.text.getvalue()

    def strip_tags(html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()

    input = get_input(text, file)
    chars = [c for c in input.replace('\r', '').replace('\n', '').strip()]
    for idx, char in enumerate(chars):
        data = get_data(char)
        if not data:
            print(f"{char}: NO HEISIG")
        else:
            print(f"{char} ({data['keyword']} | {data['keyword_ita']}): {strip_tags(data['story'])}")
        if (idx < len(chars) - 1):
            print()


@click.command()
@click.argument('text', required=False)
@click.option('-f', '--file', type=click.File('r'), default=sys.stdin)
@click.option('-m', '--max-frame', type=click.INT, default=-1, help='Max Heisig frame known.')
@click.option('-o', '--only-known', required=False, is_flag=True, help='Print only known frames.')
@click.option('-u', '--only-unknown', required=False, is_flag=True, help='Print only unknown frames.')
@click.option('-q', '--unique', required=False, is_flag=True, help='Print every character only once.')
@click.option('-t', '--format', type=click.Choice(['csv', 'json', 'tabulate']), default='csv', help='Output format (default csv).')
@click.option('-s', '--sort', type=click.Choice(['text', 'frame', 'frequency', 'occurrencies']),
              default='text', help='Sort characters by original order, heisig frame number or frequency number.')
@click.option('-c', '--frequencies-corpus', type=click.Choice(['renminwang', 'subtlexch']), default='subtlexch', help='Frequencies data corpus.')
@click.option('-r', '--reverse', required=False, is_flag=True, default=False, help='Reverse order if sorting by frame or frequency.')
@click.option('-h', '--fields', required=False, type=click.UNPROCESSED,
              default=['known', 'hanzi', 'frame', 'frequency', 'hsk', 'pinyin', 'keyword', 'occurrencies'],
              callback=validate_fields, help='Fields to show.')
@click.option('-v', '--verbose', required=False, is_flag=True)
def parse(text, file, max_frame, only_known, only_unknown, unique, format, sort, frequencies_corpus, reverse, fields, verbose):
    """
    Parses a text and returns a list of Heisig frames.

    If no text is passed as argument fallbacks to stdin then clipboard
    """
    hsg = Heisig(frequencies_corpus, max_frame)
    hsk = HSK()
    input = get_input(text, file)
    chars = [c for c in input.replace('\r', '').replace('\n', '').strip() if not hsg.is_additional_character(c)]
    statistics = hsg.get_statistics(chars)

    # select data to output based on options
    if unique:
        chars = [c for i, c in enumerate(chars) if c not in chars[:i]]  # remove duplicates
    if only_unknown:
        chars = [c for c in chars if not hsg.is_known(c)]
    elif only_known:
        chars = [c for c in chars if hsg.is_known(c)]
    if sort == 'frame' or sort == 'frequency':
        chars = sorted(chars, key=lambda x: hsg.get_frame_info(x)[sort] if x in hsg.heisig else 100000, reverse=reverse)
    elif sort == 'occurrencies':
        chars = sorted(chars, key=lambda x: statistics['frequencies'][x]['occurrencies'], reverse=not reverse)

    # prepare data for output
    data = []
    for char in chars:
        occurrencies = f"{statistics['frequencies'][char]['occurrencies']} ({statistics['frequencies'][char]['percent']}%)"
        hsk_level = hsk.get_hsk_new_char_level(char) if hsk.get_hsk_new_char_level(char) else ""
        if char in hsg.heisig:
            info = hsg.get_frame_info(char)
            # known = '' if hsg.is_known(char) else '*'
            item = {
                'known': '' if hsg.is_known(char) else '*',
                'hanzi': info['hanzi'],
                'frame': info['frame'],
                'frequency': info['frequency'],
                'hsk': hsk_level,
                'pinyin': info['pinyin'],
                'keyword': info['keyword'],
                'occurrencies': occurrencies,
            }
        else:
            item = {
                'known': 'NA',
                'hanzi': char,
                'frame': '',
                'frequency': '',
                'hsk': hsk_level,
                'pinyin': ' '.join(pinyin(char, style=Style.TONE3, heteronym=True)[0]),
                'keyword': '',
                'occurrencies': occurrencies,
            }
        # filter fields to show
        item = [item[field] for field in fields]
        data.append(item)

    # output data
    WRITERS[format](fields).writerows(data)

    # output stats
    if verbose:
        print(f"\r\nKnown characters: {statistics['known']}/{statistics['chars']} ({statistics['known_percent']}%)")
        print(f"Unknown characters: {statistics['unknown']}/{statistics['chars']} ({statistics['unknown_percent']}%)")
        print(f"Known unique characters: {statistics['known_unique']}/{statistics['chars_unique']} ({statistics['known_unique_percent']}%)")
        print(f"Unknown unique characters: {statistics['unknown_unique']}/{statistics['chars_unique']} ({statistics['unknown_unique_percent']}%)\r\n")


@click.command()
@click.argument('text', required=False)
@click.option('-f', '--file', required=False, type=click.File('r'), default=sys.stdin)
@click.option('-m', '--max-frame', type=click.INT, default=-1)
@click.option('-v', '--verbose', required=False, is_flag=True)
def enrich(text, file, max_frame, verbose):
    """
    Parses a text and highlights unknown Heisig frames (blue) and non-Heisig characters (red).

    If no text is passed as argument fallbacks to stdin then clipboard
    """
    hsg = Heisig('subtlexch', max_frame)
    hsk = HSK()
    input = get_input(text, file)
    chars = [c for c in input.strip()]
    statistics = hsg.get_statistics(chars)

    # output data
    for char in chars:
        if not hsg.is_known(char):
            if char in hsg.heisig:
                print(f"[bold blue]{char}[/bold blue]", end='')
            else:
                print(f"[bold red]{char}[/bold red]", end='')
        else:
            print(f"[bold white]{char}[/bold white]", end='')

    # output stats
    if verbose:
        print(f"\r\n\r\nKnown characters: {statistics['known']}/{statistics['chars']} ({statistics['known_percent']}%)")
        print(f"Unknown characters: {statistics['unknown']}/{statistics['chars']} ({statistics['unknown_percent']}%)")
        print(f"Known unique characters: {statistics['known_unique']}/{statistics['chars_unique']} ({statistics['known_unique_percent']}%)")
        print(f"Unknown unique characters: {statistics['unknown_unique']}/{statistics['chars_unique']} ({statistics['unknown_unique_percent']}%)\r\n")


@click.command()
@click.option('--min', type=click.INT, default=0)
@click.option('--max', type=click.INT, default=9999)
@click.option('-s', '--sort', type=click.Choice(['frame', 'frequency']), default='frame')
@click.option('-c', '--frequencies-corpus', type=click.Choice(['renminwang', 'subtlexch']), default='subtlexch', help='Frequencies data corpus.')
@click.option('-r', '--reverse', required=False, is_flag=True, default=False, help='Reverse sorting order.')
@click.option('-f', '--format', required=False, type=click.Choice(['csv', 'json', 'tabulate']), default='tabulate', help='Output format (default csv).')
@click.option('-m', '--max-results', required=False, type=click.INT, default=-1, help='Show max n results.')
def list(min, max, sort, frequencies_corpus, reverse, format, max_results):
    """
    Prints Heisig frames data.
    """
    hsg = Heisig(frequencies_corpus)
    frames = [frame for idx, frame in enumerate(hsg.heisig.values()) if idx+1 >= min and idx+1 <= max]
    if sort == 'frame' and reverse:
        frames.reverse()
    if sort == 'frequency':
        frames = sorted(frames, key=lambda x: x['frequency'], reverse=reverse)
    if max_results > -1:
        frames = frames[:max_results]
    hsg.output(frames, format)
