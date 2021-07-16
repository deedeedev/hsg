import sys
import csv
import json
import click

from frequency import Frequency
from rich import print
from tabulate import tabulate

# TODO implementare ricerca per pinyin, definizione, frequenza ecc

class Ccedict:

    def __init__(self, cedictfile):
        self.cedictfile = cedictfile
        self.dictionary = []
        self.fq = Frequency('assets/renminwang/RENMINWANG-CHR', 'assets/renminwang/RENMINWANG-WF')
        self.load_dict()

    def load_dict(self):
        with open(self.cedictfile) as f:
            text = f.read()
            lines = text.split('\n')
            self.dict_lines = list(lines)
            for line in self.dict_lines:
                self.parse_line(line)
            self.remove_surnames()

    def parse_line(self, line):
        if line == '':
            self.dict_lines.remove(line)
            return
        line = line.rstrip('/').split('/')
        if len(line) <= 1:
            return
        char_and_pinyin = line[0].split('[')
        characters = char_and_pinyin[0].split()
        frequencies = self.fq.find_word(characters[1])
        self.dictionary.append({
            'simplified': characters[1],
            'traditional': characters[0],
            'pinyin': char_and_pinyin[1].rstrip().rstrip(']'),
            'english': line[1].replace('|', '/'),
            'rank': frequencies['rank'] if frequencies else sys.maxsize,
            'count_x_cd': frequencies['count_x_cd'] if frequencies else sys.maxsize,
        })

    def remove_surnames(self):
        for x in range(len(self.dictionary)-1, -1, -1):
            if "surname " in self.dictionary[x]['english']:
                if self.dictionary[x]['traditional'] == self.dictionary[x+1]['traditional']:
                    self.dictionary.pop(x)
    
    # finds all lemmas containing specific character(s)
    def search(self, query, exact, format, max_results):
        if exact:
            words = [w for w in self.dictionary if w['simplified'] == query]
        else:
            words = [w for w in self.dictionary if query in w['simplified']]
        words = sorted(words, key=lambda x: x['rank'], reverse=False)
        # words = sorted(words, key=lambda x: x['count_x_cd'], reverse=True)
        if max_results > -1:
            words = words[:max_results]
        self.output(words, format)
    
    def output(self, words, format):
        if format == 'csv':
            fields = ('rank', 'simplified', 'traditional', 'pinyin', 'english')
            writer = csv.DictWriter(sys.stdout, fieldnames=fields, delimiter='\t', extrasaction='ignore')
            writer.writeheader()
            writer.writerows(words[:10])
        elif format == 'json':
            print(json.dumps(words))
        elif format == 'tabulate':
            for w in words:
                w.pop('count_x_cd', None)
                if len(str(w['rank'])) > 5:
                    w['rank'] = ''
                w['english'] = w['english'][:70]
            print(tabulate(words, headers='keys', tablefmt='github'))


@click.command()
@click.argument('query')
@click.option('-e', '--exact', required=False, is_flag=True, help='Search exact expression.')
@click.option('-f', '--format', required=False, type=click.Choice(['csv', 'json', 'tabulate']), default='tabulate', help='Output format (default csv).')
@click.option('-m', '--max-results', required=False, type=click.INT, default=-1, help='Show max n results.')
def search(query, exact, format, max_results):
    ce = Ccedict('assets/cedict_ts.u8')
    ce.search(query, exact, format, max_results)

if __name__ == '__main__':
    search()