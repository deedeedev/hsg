import sys
import csv

from typing import Any, Optional

from classes.frequency import Frequency
from utils.constants import SUBTLEX_CH_CHARS_CSV, SUBTLEX_CH_WORDS_CSV, SUBTLEX_CH_WORDS_POS_COMBINED_CSV

# TODO: implementare SUBTLEX_CH_WORDS_POS_COMBINED_CSV con POS


class SubtlexCh(Frequency):

    def __init__(self):
        self.char_freq: list[Any] = self.load_csv(SUBTLEX_CH_CHARS_CSV)
        self.word_freq: list[Any] = self.load_csv(SUBTLEX_CH_WORDS_CSV)
        self.chars = self.create_dict(self.char_freq)
        self.words = self.create_dict(self.word_freq)

    def load_csv(self, csvfile: str) -> list[Any]:
        with open(csvfile, 'r') as f:
            fields = ('lemma', 'count', 'count_million', 'count_log', 'cd', 'cd_percent', 'cd_log', 'rank', 'count_x_cd')
            reader = csv.DictReader(f, fieldnames=fields, delimiter='\t')
            reader_no_headers = list(reader)[3:]  # skip first 3 lines
            for idx, lemma in enumerate(reader_no_headers):
                lemma['rank'] = idx + 1  # type: ignore
                lemma['count_x_cd'] = int(lemma['count']) * int(lemma['cd'])  # type: ignore
            return reader_no_headers

    def create_dict(self, list) -> dict[str, Any]:
        dict = {}
        for l in list:
            dict[l['lemma']] = l
        return dict

    def find_char(self, char: str) -> Optional[list[Any]]:
        return self.chars.get(char)

    def find_word(self, word: str) -> Optional[list[Any]]:
        return self.words.get(word)

    def print_most_frequent_words(self, num: int) -> None:
        fields = ('rank', 'lemma', 'count', 'count_million', 'count_log', 'cd', 'cd_percent', 'cd_log', 'rank', 'count_x_cd')
        writer = csv.DictWriter(sys.stdout, fieldnames=fields, delimiter='\t')
        # sort by count*cd desc
        data = sorted(self.word_freq, key=lambda x: int(x['count']) * int(x['cd']), reverse=True)
        writer.writeheader()
        writer.writerows(data[:num])


if __name__ == '__main__':
    fq = SubtlexCh()

    # print(fq.find_char('引'))
    # print(fq.find_word('中国'))
    fq.print_most_frequent_words(10)
