# http://www.plecoforums.com/threads/media-related-vocabulary-gathering-project.6451/post-49299

import sys
import csv
import click

# TODO implementare cli


class Frequency:

    def __init__(self, char_freq_csv, word_freq_csv):
        self.char_freq = self.load_csv(char_freq_csv)
        self.word_freq = self.load_csv(word_freq_csv)
        self.chars = self.create_dict(self.char_freq)
        self.words = self.create_dict(self.word_freq)

    """
    cd -> corpus documents

    count: numero di volte in cui appare il lemma nell'intero corpus
    count_million: numero di volte in cui appare il lemma per milione di parole nell'intero corpus
    count_log: numero di volte in cui appare il lemma nell'intero corpus su scala logaritmica
    cd: numero di documenti in cui appare il lemma
    cd_percent: percentuale di documenti in cui appare il lemma
    cd_log: numero di documenti in cui appare il lemma su scala logaritmica
    """

    def load_csv(self, csvfile):
        with open(csvfile, 'r') as f:
            fields = ('lemma', 'count', 'count_million', 'count_log', 'cd', 'cd_percent', 'cd_log', 'rank', 'count_x_cd')
            reader = csv.DictReader(f, fieldnames=fields, delimiter='\t')
            reader = list(reader)[3:]  # skip first 3 lines
            for idx, lemma in enumerate(reader):
                lemma['rank'] = idx + 1
                lemma['count_x_cd'] = int(lemma['count']) * int(lemma['cd'])
            return reader
    
    def create_dict(self, list):
        dict = {}
        for l in list:
            dict[l['lemma']] = l
        return dict
    
    def find_char(self, char):
        return self.chars.get(char)

    def find_word(self, word):
        return self.words.get(word)
    
    def get_most_frequent_words(self, num):
        fields = ('rank', 'lemma', 'count', 'count_million', 'count_log', 'cd', 'cd_percent', 'cd_log', 'rank', 'count_c_cd')
        writer = csv.DictWriter(sys.stdout, fieldnames=fields, delimiter='\t')
        # sort by count*cd desc
        data = sorted(self.word_freq, key = lambda x: int(x['count']) * int(x['cd']), reverse=True)
        writer.writeheader()
        writer.writerows(data[:num])


if __name__ == '__main__':
    fq = Frequency(
        'assets/renminwang/RENMINWANG-CHR',
        'assets/renminwang/RENMINWANG-WF',
    )

    print(fq.find_char('引'))
    # print(fq.find_word('中国'))
    # fq.get_most_frequent_words(10)