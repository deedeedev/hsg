from classes.subtlexch import SubtlexCh
import sys
import csv
import json
import re

from classes.renminwang import RenMinWang
from classes.hsk import HSK
from rich import print
from tabulate import tabulate
from utils.constants import ADDITIONAL_CHARACTERS

from enum import Enum
from typing import List, Union


class QueryType(Enum):

    SIMPLIFIED = 'simplified'
    PINYIN = 'pinyin'
    ENGLISH = 'english'


class Ccedict:

    def __init__(self, cedictfile: str, frequencies_corpus: str) -> None:
        self.cedictfile: str = cedictfile
        self.dictionary: List[dict] = []
        self.fq = {'renminwang': RenMinWang, 'subtlexch': SubtlexCh}[frequencies_corpus]()
        self.hsk: HSK = HSK()
        self.load_dict()

    def load_dict(self) -> None:
        with open(self.cedictfile) as f:
            text: str = f.read()
            lines: List[str] = text.split('\n')
            self.dict_lines = list(lines)
            for line in self.dict_lines:
                self.parse_line(line)
            self.remove_surnames()

    def parse_line(self, line: str) -> None:
        if line == '':
            self.dict_lines.remove(line)
            return
        line_parts = line.rstrip('/').split('/')
        if len(line_parts) <= 1:
            return
        char_and_pinyin: List[str] = line_parts[0].split('[')
        characters: List[str] = char_and_pinyin[0].split()
        frequencies = self.fq.find_word(characters[1])
        hsk_level = self.hsk.get_hsk_new_word_level(characters[1])
        self.dictionary.append({
            'simplified': characters[1],
            'traditional': characters[0],
            'pinyin': char_and_pinyin[1].rstrip().rstrip(']'),
            'english': line_parts[1].replace('|', '/'),
            'hsk': hsk_level if hsk_level else '',
            'frequency': frequencies['rank'] if frequencies else '',
            'count_x_cd': frequencies['count_x_cd'] if frequencies else '',
        })

    def remove_surnames(self) -> None:
        for x in range(len(self.dictionary)-1, -1, -1):
            if "surname " in self.dictionary[x]['english']:
                if self.dictionary[x]['traditional'] == self.dictionary[x+1]['traditional']:
                    self.dictionary.pop(x)

    def get_query_type(self, query: str) -> str:
        pattern_hanzi = re.compile(
            '^[^' + ADDITIONAL_CHARACTERS.replace('[', '\[').replace(']', '\]') + ']*$')
        pattern_pinyin: re.Pattern = re.compile('[a-z:]{2,5}\d')
        if pattern_hanzi.match(query):
            return QueryType.SIMPLIFIED.value
        elif pattern_pinyin.match(query):
            return QueryType.PINYIN.value
        else:
            return QueryType.ENGLISH.value

    # finds all lemmas containing specific character(s)
    def search(self, query: str, exact: bool, show_traditional: bool, format: str, sort: str, reverse: bool, max_hsk: str, max_results: int, all_results: bool) -> None:
        search_field: str = self.get_query_type(query)
        query = query.replace(' ', '').lower()

        words: List[dict] = []
        if exact:
            words = [w for w in self.dictionary if w[search_field].replace(' ', '').lower() == query]
        else:
            words = [w for w in self.dictionary if query in w[search_field].replace(' ', '').lower()]

        # filter results by hsk level
        if max_hsk:
            if max_hsk == '7':
                max_hsk = '7-9'
            words = [w for w in words if w['hsk'] and w['hsk'] <= max_hsk]

        # sort results
        words = sorted(words, key=lambda x: self.sort_key(x[sort]), reverse=reverse)

        if not show_traditional:
            for w in words:
                del w['traditional']

        if not all_results and max_results > 0:
            words = words[:max_results]

        self.output(words, format)

    def sort_key(self, value: Union[str, int]):
        if value == '7-9':
            return 7
        return int(value) if value else sys.maxsize

    def output(self, words: List[dict], format: str) -> None:
        if format == 'csv':
            writer: csv.DictWriter = csv.DictWriter(
                sys.stdout, fieldnames=list(words[0].keys()), delimiter='\t', extrasaction='ignore')
            writer.writeheader()
            writer.writerows(words[:10])
        elif format == 'json':
            print(json.dumps(words))
        elif format == 'tabulate':
            for w in words:
                w.pop('count_x_cd', None)
                if len(str(w['frequency'])) > 5:
                    w['frequency'] = ''
                w['english'] = w['english'][:70]
            print(tabulate(words, headers='keys', tablefmt='github'))
