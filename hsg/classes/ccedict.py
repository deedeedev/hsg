import csv
import json
import logging
import os
import pickle
import re
import sys
from enum import Enum
from typing import Any

from rich import print
from tabulate import tabulate

from hsg.classes.frequency import Frequency
from hsg.classes.frequency_factory import create_frequency
from hsg.classes.hsk import HSK
from hsg.utils.constants import ADDITIONAL_CHARACTERS, ASSETS_DIR_PATH

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Query classification for CC-CEDICT search: simplified, pinyin, or english."""

    SIMPLIFIED = 'simplified'
    PINYIN = 'pinyin'
    ENGLISH = 'english'


class Ccedict:
    """CC-CEDICT dictionary reader with HSK and frequency enrichment.

    Loads the dictionary from a cedict_ts.u8 file (or a pickled cache).
    Supports search by simplified characters, pinyin, or English gloss,
    with optional HSK-level and frequency-rank filtering/sorting.
    """

    def __init__(self, cedictfile: str, frequencies_corpus: str) -> None:
        """Load the CC-CEDICT dictionary and initialise HSK + frequency backends."""
        self.cedictfile: str = cedictfile
        self.dictionary: list[dict[str, Any]] = []
        self.fq: Frequency = create_frequency(frequencies_corpus)
        self.hsk: HSK = HSK()
        self.dict_lines: list[str] = []
        self.load_dict()

    def load_dict(self) -> None:
        """Load the dictionary from pickle cache or parse the raw .u8 file."""
        pickle_dict = os.path.join(ASSETS_DIR_PATH, 'ccedict.pickle')
        if os.path.isfile(pickle_dict):
            with open(pickle_dict, 'rb') as d:
                loaded: list[dict[str, Any]] = pickle.load(d)
                self.dictionary = loaded
                logger.info('Loaded ccedict from pickle (%d entries)', len(self.dictionary))
                return
        logger.info('Building ccedict pickle from %s', self.cedictfile)
        with open(self.cedictfile) as f:
            text: str = f.read()
            lines: list[str] = text.split('\n')
            self.dict_lines = list(lines)
            for line in self.dict_lines:
                self.parse_line(line)
            self.remove_surnames()
            with open(pickle_dict, 'wb') as d:
                pickle.dump(self.dictionary, d)

    def parse_line(self, line: str) -> None:
        """Parse a single CC-CEDICT line and append to self.dictionary."""
        if line == '':
            self.dict_lines.remove(line)
            return
        line_parts = line.rstrip('/').split('/')
        if len(line_parts) <= 1:
            return
        char_and_pinyin: list[str] = line_parts[0].split('[')
        characters: list[str] = char_and_pinyin[0].split()
        frequencies = self.fq.find_word(characters[1])
        hsk_level = self.hsk.get_hsk_new_word_level(characters[1])
        self.dictionary.append(
            {
                'simplified': characters[1],
                'traditional': characters[0],
                'pinyin': char_and_pinyin[1].rstrip().rstrip(']'),
                'english': line_parts[1].replace('|', '/'),
                'hsk': hsk_level if hsk_level else '',
                'frequency': frequencies['rank'] if frequencies else '',
                'count_x_cd': frequencies['count_x_cd'] if frequencies else '',
            }
        )

    def remove_surnames(self) -> None:
        """Filter out surname entries from the dictionary."""
        for x in range(len(self.dictionary) - 1, -1, -1):
            entry = self.dictionary[x]
            if 'surname ' in entry['english'] and entry['traditional'] == self.dictionary[x + 1]['traditional']:
                self.dictionary.pop(x)

    def get_query_type(self, query: str) -> str:
        """Classify a query string as 'simplified', 'pinyin', or 'english'."""
        pattern_hanzi: re.Pattern[str] = re.compile(
            '^[^' + ADDITIONAL_CHARACTERS.replace('[', r'\[').replace(']', r'\]') + ']*$'
        )
        pattern_pinyin: re.Pattern[str] = re.compile(r'[a-z:]{2,5}\d')
        if pattern_hanzi.match(query):
            return QueryType.SIMPLIFIED.value
        elif pattern_pinyin.match(query):
            return QueryType.PINYIN.value
        else:
            return QueryType.ENGLISH.value

    def search(
        self,
        query: str,
        exact: bool,
        show_traditional: bool,
        format: str,
        sort: str,
        reverse: bool,
        max_hsk: str,
        max_results: int,
        all_results: bool,
    ) -> None:
        """Search the dictionary and print results in the chosen format."""
        search_field: str = self.get_query_type(query)
        query = query.replace(' ', '').lower()

        words: list[dict[str, Any]] = []
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

    def sort_key(self, value: str | int) -> int:
        """Return a numeric sort key for HSK level or frequency rank."""
        if value == '7-9':
            return 7
        return int(value) if value else sys.maxsize

    def output(self, words: list[dict[str, Any]], format: str) -> None:
        """Print search results in the specified format (csv, json, tabulate)."""
        if format == 'csv':
            writer: csv.DictWriter[str] = csv.DictWriter(
                sys.stdout, fieldnames=list(words[0].keys()), delimiter='\t', extrasaction='ignore'
            )
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
