import os
import sys
import csv
import json
import random
import click

from rich import print

# TODO utilizzare click per l'output colorato al posto di rich (https://click.palletsprojects.com/en/8.0.x/utils/#ansi-colors)


class TatoebaHeisig:

    ADDITIONAL_CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!?#%()[]-_,;:.=\'"“”１６８！。？，、；：％（）《》〈〉【】〖〗〔〕「」『』—'

    def __init__(self, tatoebacsv, heisigcsv, maxframe):
        self.tatoebacsv = tatoebacsv
        self.heisigcsv = heisigcsv
        self.maxframe = maxframe
        self.tatoeba = {}
        self.heisig = {}
        self.allowed_sentences = []

    def load_tatoeba(self):
        with open(self.tatoebacsv) as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                hanzi = row[1]
                english = row[3]
                if not hanzi in self.tatoeba:
                    self.tatoeba[hanzi] = [english]
                else:
                    self.tatoeba[hanzi].append(english)

    def load_heisig(self):
        with open(self.heisigcsv) as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                frame = row[2]
                if frame.startswith("v") or not frame:
                    continue
                frame = int(frame)
                hanzi = row[0]
                keyword = row[4]
                pinyin = row[5]
                self.heisig[hanzi] = {
                    "frame": frame,
                    "keyword": keyword,
                    "pinyin": pinyin,
                }

    def get_allowed_frames(self):
        return [hanzi for hanzi in self.heisig if self.heisig[hanzi]["frame"] <= self.maxframe]

    def get_allowed_characters(self):
        return self.get_allowed_frames() + [char for char in self.ADDITIONAL_CHARACTERS]

    def get_all_allowed_sentences(self):
        self.load_tatoeba()
        self.load_heisig()
        count = 0
        allowed = self.get_allowed_characters()
        for sentence in self.tatoeba:
            if all([True if char in allowed else False for char in sentence]):
                self.allowed_sentences.append({"hanzi": sentence, "translations": self.tatoeba[sentence]})
                count += 1

    # find all allowed sentences containing keyword
    def find_sentences(self, keyword, max_sentences, reverse):
        if not self.allowed_sentences:
            self.get_all_allowed_sentences()
        sentences = [sentence for sentence in self.allowed_sentences if keyword in sentence["hanzi"]]
        # longer sentences first
        return sorted(sentences, key=lambda kv: len(kv["hanzi"]), reverse=reverse)[:max_sentences-1]

    # get n allowed sentences of length >= minlength
    def find_random_sentences(self, number, minlength, reverse):
        if not self.allowed_sentences:
            self.get_all_allowed_sentences()
        minlength_sentences = [sentence for sentence in self.allowed_sentences if len(sentence["hanzi"]) >= minlength]
        minlength_sentences = random.sample(minlength_sentences, number)
        return sorted(minlength_sentences, key=lambda kv: len(kv["hanzi"]), reverse=reverse)
    
    def print_sentences(self, sentences, format):
        # print(sentences)
        if format == 'csv':
            writer = csv.writer(sys.stdout, delimiter='\t')
            for s in sentences:
                writer.writerow([s['hanzi'],''.join(s['translations'])])
        elif format == 'json':
            print(json.dumps(sentences))


@click.group()
def cli():
    pass


@cli.command()
@click.argument('keyword')
@click.option('-m', '--max-frame', type=click.INT, default=1500, help='Max Heisig frame known. (default 1500)')
@click.option('-n', '--max-sentences', type=click.INT, default=10000, help='Max sentences to return (default ALL)')
@click.option('-r', '--reverse', required=False, is_flag=True, default=False, help='Return longer sentences first (default FALSE)')
@click.option('-f', '--format', type=click.Choice(['csv','json']), default='csv', help='Output format (default csv).')
def sentences(keyword, max_frame, max_sentences, reverse, format):
    """
    Returns all sentences from the Tatoeba corpus with the specified keyword

    python heisigtatoeba.py sentences -m 1500 -n 20 "爱"
    """
    ht = TatoebaHeisig("assets/tatoeba.tsv", "assets/heisig.tsv", max_frame)
    sentences = ht.find_sentences(keyword, max_sentences, reverse)
    ht.print_sentences(sentences, format)


@cli.command(name='random')
@click.option('-m', '--max-frame', type=click.INT, default=1500, help='Max Heisig frame known.')
@click.option('-n', '--sentences-number', type=click.INT, default=10, help='Return n sentences (default 10).')
@click.option('-l', '--min-length', type=click.INT, default=10, help='Return only sentences of length l or above (default 10).')
@click.option('-r', '--reverse', required=False, is_flag=True, default=False, help='Return longer sentences first (default FALSE)')
@click.option('-f', '--format', type=click.Choice(['csv','json']), default='csv', help='Output format (default csv).')
def random_sentences(max_frame, sentences_number, min_length, reverse, format):
    """
    Returns random sentences from the Tatoeba corpus with the specified keyword

    python heisigtatoeba.py sentences -m 1500 -n 10 -l 10
    """
    ht = TatoebaHeisig("assets/tatoeba.tsv", "assets/heisig.tsv", max_frame)
    sentences = ht.find_random_sentences(sentences_number, min_length, reverse)
    ht.print_sentences(sentences, format)


if __name__ == "__main__":
    cli()