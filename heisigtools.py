# character frequencies: https://lingua.mtsu.edu/chinese-computing/statistics/char/list.php?Which=MO

import os
import sys
import csv
import json
# import codecs
import click
import clipboard

from collections import OrderedDict
from rich import print
from tabulate import tabulate


class HeisigTools:

    ADDITIONAL_CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!?#%()[]-_,;:.=\'"“”１６８！。？，、；：％（）《》〈〉【】〖〗〔〕「」『』—'

    def __init__(self, heisigcsv, frequenciescsv, maxframe=3225):
        self.heisigcsv = heisigcsv
        self.frequenciescsv = frequenciescsv
        self.maxframe = maxframe
        self.frequencies = {}
        self.heisig = {}
        self.load_frequencies()
        self.load_heisig()
        self.known_characters = self.get_known_characters()

    def set_max_frame(self, maxframe):
        self.maxframe = maxframe

    def load_heisig(self):
        with open(self.heisigcsv) as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                frame = row[2]
                if frame.startswith('v') or not frame:
                    continue
                frame = int(frame)
                hanzi = row[0]
                keyword = row[4]
                pinyin = row[5]
                frequency = self.frequencies[hanzi] if hanzi in self.frequencies else 9999
                self.heisig[hanzi] = {
                    'hanzi': hanzi,
                    'frame': frame,
                    'keyword': keyword,
                    'pinyin': pinyin,
                    'frequency': frequency,
                }

    def load_frequencies(self):
        with open(self.frequenciescsv, 'r', encoding='utf-8') as f:
            # text = codecs.decode(f.read().encode(), 'utf-8-sig')
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.frequencies[row[1]] = int(row[0])

    def get_known_frames(self):
        return [hanzi for hanzi in self.heisig if self.heisig[hanzi]['frame'] <= self.maxframe]

    def get_known_characters(self):
        return self.get_known_frames() + [char for char in self.ADDITIONAL_CHARACTERS]

    def is_known(self, char):
        return char in self.known_characters

    def is_additional_character(self, char):
        return char in self.ADDITIONAL_CHARACTERS

    def get_frame_info(self, char):
        return self.heisig[char]

    def get_statistics(self, chars):
        unique_chars = [c for i, c in enumerate(chars) if c not in chars[:i]]  # remove duplicates
        total_chars = len(chars)
        total_chars_unique = len(unique_chars)
        total_known = len([c for c in chars if self.is_known(c)])
        total_known_unique = len([c for c in unique_chars if self.is_known(c)])
        total_known_percent = round(total_known / total_chars * 100, 2) if total_chars > 0 else 0
        total_known_unique_percent = round(total_known_unique / total_chars_unique *
                                           100, 2) if total_chars_unique > 0 else 0
        return {
            'chars': total_chars,
            'known': total_known,
            'known_percent': total_known_percent,
            'chars_unique': total_chars_unique,
            'known_unique': total_known_unique,
            'known_unique_percent': total_known_unique_percent,
        }

    def output(self, words, format):
        if format == 'csv':
            fields = ('hanzi', 'frame', 'keyword', 'pinyin', 'frequency')
            writer = csv.DictWriter(sys.stdout, fieldnames=fields, delimiter='\t', extrasaction='ignore')
            writer.writeheader()
            writer.writerows(words[:10])
        elif format == 'json':
            print(json.dumps(words))
        elif format == 'tabulate':
            print(tabulate(words, headers='keys', tablefmt='github'))


@click.group()
def cli():
    pass


@cli.command()
@click.argument('text', required=False)
@click.option('-f', '--file', type=click.File('r'), default=sys.stdin)
@click.option('-m', '--max-frame', type=click.INT, default=1500, help='Max Heisig frame known.')
@click.option('-o', '--only-known', required=False, is_flag=True, help='Print only known frames.')
@click.option('-u', '--only-unknown', required=False, is_flag=True, help='Print only unknown frames.')
@click.option('-q', '--unique', required=False, is_flag=True, help='Print every character only once.')
@click.option('-t', '--format', type=click.Choice(['csv', 'json']), default='csv', help='Output format (default csv).')
@click.option('-s', '--sort', type=click.Choice(['text', 'frame', 'frequency']), default='text', help='Sort characters by original order, heisig frame number or frequency number')
@click.option('-r', '--reverse', required=False, is_flag=True, default=False, help='Reverse order if sorting by frame or frequency')
@click.option('-v', '--verbose', required=False, is_flag=True)
def parse(text, file, max_frame, only_known, only_unknown, unique, format, sort, reverse, verbose):
    """
    Parses a text and returns a list of Heisig frames.

    If no text is passed as argument fallbacks to stdin then clipboard
    """
    ht = HeisigTools("assets/heisig.tsv", "assets/hanzi_by_frequency.csv", max_frame)
    input = get_input(text, file)
    chars = [c for c in input.replace('\r', '').replace('\n', '').strip() if not ht.is_additional_character(c)]
    statistics = ht.get_statistics(chars)
    if unique:
        chars = [c for i, c in enumerate(chars) if c not in chars[:i]]  # remove duplicates
    if sort == 'frame' or sort == 'frequency':
        chars = sorted(chars, key=lambda x: ht.get_frame_info(
            x)[sort] if x in ht.heisig else 100000, reverse=reverse)
    if format == 'csv':
        writer = csv.writer(sys.stdout, delimiter='\t')
        writer.writerow(['known', 'hanzi', 'frame', 'frequency', 'pinyin', 'keyword'])
        for char in chars:
            is_known = ht.is_known(char)
            if only_known and not is_known:
                continue
            if only_unknown and is_known:
                continue
            if char in ht.heisig:
                info = ht.get_frame_info(char)
                known = "" if is_known else "*"
                writer.writerow([known, info['hanzi'], info['frame'],
                                info['frequency'], info['pinyin'], info['keyword']])
            else:
                writer.writerow(["NA", char, "", "", "", "", ""])
    elif format == 'json':
        data = []
        for char in chars:
            if only_known and not ht.is_known(char):
                continue
            if only_unknown and ht.is_known(char):
                continue
            if char in ht.heisig:
                info = ht.get_frame_info(char)
                data.append(info)
            else:
                data.append([char, "NA", "NA", "NA", "NA"])
        print(json.dumps(data))
    if verbose:
        print(f"\r\nKnown characters: {statistics['known']}/{statistics['chars']} ({statistics['known_percent']}%)")
        print(
            f"Known unique characters: {statistics['known_unique']}/{statistics['chars_unique']} ({statistics['known_unique_percent']}%)\r\n")


@cli.command()
@click.argument('text', required=False)
@click.option('-f', '--file', required=False, type=click.File('r'), default=sys.stdin)
@click.option('-m', '--max-frame', type=click.INT, default=1500)
@click.option('-v', '--verbose', required=False, is_flag=True)
def enrich(text, file, max_frame, verbose):
    """
    Parses a text and highlights unknown Heisig frames (blue) and non-Heisig characters (red).

    If no text is passed as argument fallbacks to stdin then clipboard
    """
    ht = HeisigTools("assets/heisig.tsv", "assets/hanzi_by_frequency.csv", max_frame)
    input = get_input(text, file)
    chars = [c for c in input.strip()]
    statistics = ht.get_statistics(chars)
    for char in chars:
        if not ht.is_known(char):
            if char in ht.heisig:
                print(f"[bold blue]{char}[/bold blue]", end='')
            else:
                print(f"[bold red]{char}[/bold red]", end='')
        else:
            print(f"[bold white]{char}[/bold white]", end='')
    if verbose:
        print(f"\r\n\r\nKnown characters: {statistics['known']}/{statistics['chars']} ({statistics['known_percent']}%)")
        print(
            f"Known unique characters: {statistics['known_unique']}/{statistics['chars_unique']} ({statistics['known_unique_percent']}%)\r\n")


@cli.command()
@click.option('--min', type=click.INT, default=0)
@click.option('--max', type=click.INT, default=9999)
@click.option('-s', '--sort', type=click.Choice(['frame', 'frequency']), default='frame')
@click.option('-r', '--reverse', required=False, is_flag=True, default=False, help='Reverse sorting order.')
@click.option('-f', '--format', required=False, type=click.Choice(['csv', 'json', 'tabulate']), default='tabulate', help='Output format (default csv).')
@click.option('-m', '--max-results', required=False, type=click.INT, default=-1, help='Show max n results.')
def list(min, max, sort, reverse, format, max_results):
    """
    Prints Heisig frames data.
    """
    ht = HeisigTools("assets/heisig.tsv", "assets/hanzi_by_frequency.csv")
    frames = [frame for idx, frame in enumerate(ht.heisig.values()) if idx+1 >= min and idx+1 <= max]
    if sort == 'frame' and reverse:
        frames.reverse()
    if sort == 'frequency':
        frames = sorted(frames, key=lambda x: x['frequency'], reverse=reverse)
    if max_results > -1:
        frames = frames[:max_results]
    ht.output(frames, format)


def get_input(text, file):
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
    cli()
