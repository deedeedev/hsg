import sys
import csv
import json

from tabulate import tabulate
from typing import Union

from classes.renminwang import RenMinWang
from classes.subtlexch import SubtlexCh
from utils.constants import HEISIG_CSV, ADDITIONAL_CHARACTERS


class Heisig:

    def __init__(self, frequencies_corpus: str, maxframe: int=-1):
        self.maxframe = maxframe
        self.frequencies = {'renminwang': RenMinWang, 'subtlexch': SubtlexCh}[frequencies_corpus]()
        self.heisig: dict[str, Union[str, int]] = {}
        self.load_heisig()
        self.known_characters = self.get_known_characters()

    def set_max_frame(self, maxframe):
        self.maxframe = maxframe

    def load_heisig(self):
        with open(HEISIG_CSV) as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                frame = row[2]
                if frame.startswith('v') or not frame:
                    continue
                frame = int(frame)
                hanzi = row[0]
                keyword = row[4]
                pinyin = row[5]
                frequency_data = self.frequencies.find_char(hanzi)
                self.heisig[hanzi] = {
                    'hanzi': hanzi,
                    'frame': frame,
                    'keyword': keyword,
                    'pinyin': pinyin,
                    'frequency': frequency_data['rank'] if frequency_data else 9999,
                }
        if self.maxframe == -1:
            self.maxframe = max([f['frame'] for f in self.heisig.values()])

    def get_known_frames(self):
        return [hanzi for hanzi in self.heisig if self.heisig[hanzi]['frame'] <= self.maxframe]

    def get_known_characters(self):
        return self.get_known_frames() + [char for char in ADDITIONAL_CHARACTERS]

    def is_known(self, char):
        return char in self.known_characters

    def is_additional_character(self, char):
        return char in ADDITIONAL_CHARACTERS

    def get_frame_info(self, char):
        return self.heisig[char]

    def get_statistics(self, chars):
        unique_chars = [c for i, c in enumerate(chars) if c not in chars[:i]]  # remove duplicates
        total_chars = len(chars)
        total_chars_unique = len(unique_chars)
        total_known = len([c for c in chars if self.is_known(c)])
        total_known_unique = len([c for c in unique_chars if self.is_known(c)])
        total_known_percent = round(total_known / total_chars * 100, 2) if total_chars > 0 else 0
        total_known_unique_percent = round(total_known_unique / total_chars_unique * 100, 2) if total_chars_unique > 0 else 0
        frequencies = {}
        for c in chars:
            if not c in frequencies:
                frequencies[c] = {'occurrencies': 1, 'percent': None, }
            else:
                frequencies[c]['occurrencies'] += 1
        for c in frequencies:
            frequencies[c]['percent'] = round(frequencies[c]['occurrencies'] / len(chars) * 100, 2)
        return {
            'chars': total_chars,
            'known': total_known,
            'known_percent': total_known_percent,
            'unknown': total_chars - total_known,
            'unknown_percent': round(100 - total_known_percent, 2),
            'chars_unique': total_chars_unique,
            'known_unique': total_known_unique,
            'known_unique_percent': total_known_unique_percent,
            'unknown_unique': total_chars_unique - total_known_unique,
            'unknown_unique_percent': round(100 - total_known_unique_percent, 2),
            'frequencies': frequencies,
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
