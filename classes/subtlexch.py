import csv

from operator import xor
from typing import Any, Optional

from classes.frequency import Frequency
from utils.constants import SUBTLEX_CH_CHARS_CSV, SUBTLEX_CH_WORDS_CSV, SUBTLEX_CH_WORDS_POS_COMBINED_CSV, HEISIG_CSV


class SubtlexCh(Frequency):

    FIELDS = ('lemma', 'count', 'count_million', 'count_log', 'cd', 'cd_percent', 'cd_log', 'rank', 'count_x_cd')
    FIELDS_POS = ('lemma', 'length', 'pinyin', 'pinyin_input', 'count', 'count_million', 'count_log', 'cd', 'cd_percent',
                  'cd_log', 'dominant_pos', 'dominant_pos_freq', 'all_pos', 'all_pos_freq', 'translation', 'rank', 'count_x_cd')
    POS = {
        'a': 'adjective',
        'ad': 'adjective as adverbial',
        'ag': 'adjective morpheme',
        'an': 'adjective with nominal function',
        'b': 'non-predicate adjective',
        'c': 'conjunction',
        'd': 'adverb',
        'dg': 'adverb morpheme',
        'e': 'interjection',
        'f': 'directional locality',
        'g': 'morpheme',
        'h': 'prefix',
        'i': 'idiom',
        'j': 'abbreviation',
        'k': 'suffix',
        'l': 'fixed expressions',
        'm': 'numeral',
        'mg': 'numeric morpheme',
        'n': 'common noun',
        'ng': 'noun morpheme',
        'nr': 'personal name',
        'ns': 'place name',
        'nt': 'organization name',
        'nx': 'nominal character string',
        'nz': 'other proper noun',
        'o': 'onomatopoeia',
        'p': 'preposition',
        'q': 'classifier',
        'r': 'pronoun',
        'rg': 'pronoun morpheme',
        's': 'space word',
        't': 'time word',
        'tg': 'time word morpheme',
        'u': 'auxiliary',
        'v': 'verb',
        'vd': 'verb as adverbial',
        'vg': 'verb morpheme',
        'vn': 'verb with nominal function',
        'w': 'symbol and non-sentential punctuation',
        'x': 'unclassified items',
        'y': 'modal particle',
        'z': 'descriptive',
    }

    def __init__(self):
        self.char_freq: list[Any] = self.load_csv(SUBTLEX_CH_CHARS_CSV, self.FIELDS)
        self.word_freq: list[Any] = self.load_csv(SUBTLEX_CH_WORDS_CSV, self.FIELDS)
        self.word_pos_freq: list[Any] = self.load_csv(SUBTLEX_CH_WORDS_POS_COMBINED_CSV, self.FIELDS_POS)
        self.chars = self.create_dict(self.char_freq)
        self.words = self.create_dict(self.word_freq)
        self.words_pos = self.create_dict(self.word_pos_freq)

    def load_csv(self, csvfile: str, fields: list[str]) -> list[Any]:
        with open(csvfile, 'r') as f:
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

    def find_pos(self, word: str) -> Optional[tuple[str, dict[str, int]]]:
        data = self.words_pos.get(word)
        if data:
            all_pos = [p for p in data['all_pos'].split('.') if p]
            all_pos_freq = [int(f) for f in data['all_pos_freq'].split('.') if f]
            all_pos_dict = {all_pos[i]: all_pos_freq[i] for i in range(len(all_pos))}
            return (data['dominant_pos'], all_pos_dict)
        return None

    def get_words_by_pos(self, pos: str, strict: bool = True):
        if strict:
            return [w for w in self.word_pos_freq if w['dominant_pos'] == pos]
        else:
            return [w for w in self.word_pos_freq if pos in [p.lower() for p in w['all_pos'].split('.')]]

    def get_most_frequent_lemmas(self, type: str = 'chars', num: int = -1, skip_heisig: bool = False, only_heisig: bool = False, min_length: int = 1, sort: str = 'rank',
                                 reverse: bool = False) -> list[Any]:
        # chars / words
        if type == 'chars':
            lemmas = self.char_freq
        else:
            lemmas = self.word_freq
        if num == -1:
            num = len(lemmas)
        # skip heisig characters?
        if xor(skip_heisig, only_heisig):
            with open(HEISIG_CSV, 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                heisig_characters = [r[0] for r in reader]
            if skip_heisig:
                lemmas = [l for l in lemmas if not l['lemma'] in heisig_characters]
            if only_heisig:
                lemmas = [l for l in lemmas if l['lemma'] in heisig_characters]
        # minimum length
        if min_length > 1:
            lemmas = [l for l in lemmas if len(l['lemma']) >= min_length]
            # lemmas = list(filter(lambda x: len(x['lemma']) >= min_length, lemmas))
        lemmas = sorted(lemmas, key=lambda x: x[sort], reverse=reverse)
        return lemmas[:num]


if __name__ == '__main__':
    fq = SubtlexCh()

    # print(fq.find_char('引'))
    # print(fq.find_word('中国'))
    # fq.print_most_frequent_words(10)

    # print(fq.find_pos('中国'))
    # print(fq.find_pos('爱好'))
    # print(fq.find_pos('奥'))
    # print(fq.find_pos('继续'))

    # data = [(pos, len(fq.get_words_by_pos(pos))) for pos in fq.POS]
    # for p in sorted(data, key=lambda x: x[1], reverse=True):
    #     print(p)

    for w in fq.get_words_by_pos('rg'):
        print(w['rank'], w['lemma'], w['translation'])
