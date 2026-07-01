import csv
import json
import sys
from typing import Any

from tabulate import tabulate

from hsg.classes.frequency import Frequency
from hsg.classes.renminwang import RenMinWang
from hsg.classes.subtlexch import SubtlexCh
from hsg.utils.constants import ADDITIONAL_CHARACTERS, HEISIG_CSV


class Heisig:
    def __init__(self, frequencies_corpus: str, maxframe: int = -1) -> None:
        self.maxframe = maxframe
        self.frequencies: Frequency = {'renminwang': RenMinWang, 'subtlexch': SubtlexCh}[frequencies_corpus]()
        self.heisig: dict[str, dict[str, Any]] = {}
        self.load_heisig()
        self.known_characters: list[str] = self.get_known_characters()

    def set_max_frame(self, maxframe: int) -> None:
        self.maxframe = maxframe

    def load_heisig(self) -> None:
        with open(HEISIG_CSV) as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                frame = row[2]
                if frame.startswith('v') or not frame:
                    continue
                frame_num = int(frame)
                hanzi = row[0]
                keyword = row[4]
                pinyin = row[5]
                frequency_data = self.frequencies.find_char(hanzi)
                self.heisig[hanzi] = {
                    'hanzi': hanzi,
                    'frame': frame_num,
                    'keyword': keyword,
                    'pinyin': pinyin,
                    'frequency': frequency_data['rank'] if frequency_data else 9999,
                }
        if self.maxframe == -1:
            self.maxframe = max([f['frame'] for f in self.heisig.values()])

    def get_known_frames(self) -> list[str]:
        return [hanzi for hanzi in self.heisig if self.heisig[hanzi]['frame'] <= self.maxframe]

    def get_known_characters(self) -> list[str]:
        return self.get_known_frames() + list(ADDITIONAL_CHARACTERS)

    def is_known(self, char: str) -> bool:
        return char in self.known_characters

    def is_additional_character(self, char: str) -> bool:
        return char in ADDITIONAL_CHARACTERS

    def get_frame_info(self, char: str) -> dict[str, Any]:
        return self.heisig[char]

    def get_statistics(self, chars: list[str]) -> dict[str, Any]:
        unique_chars = [c for i, c in enumerate(chars) if c not in chars[:i]]  # remove duplicates
        total_chars = len(chars)
        total_chars_unique = len(unique_chars)
        total_known = len([c for c in chars if self.is_known(c)])
        total_known_unique = len([c for c in unique_chars if self.is_known(c)])
        total_known_percent = round(total_known / total_chars * 100, 2) if total_chars > 0 else 0
        total_known_unique_percent = (
            round(total_known_unique / total_chars_unique * 100, 2) if total_chars_unique > 0 else 0
        )
        frequencies: dict[str, dict[str, Any]] = {}
        for c in chars:
            if c not in frequencies:
                frequencies[c] = {
                    'occurrencies': 1,
                    'percent': None,
                }
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

    def output(self, words: list[dict[str, Any]], format: str) -> None:
        if format == 'csv':
            fields = ('hanzi', 'frame', 'keyword', 'pinyin', 'frequency')
            writer: csv.DictWriter[str] = csv.DictWriter(
                sys.stdout, fieldnames=fields, delimiter='\t', extrasaction='ignore'
            )
            writer.writeheader()
            writer.writerows(words)
        elif format == 'json':
            print(json.dumps(words))
        elif format == 'tabulate':
            print(tabulate(words, headers='keys', tablefmt='github'))
