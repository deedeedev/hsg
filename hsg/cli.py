import click

from hsg.commands.ccedictsearch import search as lookup
from hsg.commands.frequencytools import search as freq
from hsg.commands.heisigtatoeba import random_sentences, sentences
from hsg.commands.heisigtools import enrich, list_frames, parse, stories


@click.group()
def cli() -> None:
    pass


cli.add_command(parse)
cli.add_command(enrich)
cli.add_command(list_frames)
cli.add_command(stories)
cli.add_command(sentences)
cli.add_command(random_sentences)
cli.add_command(lookup)
cli.add_command(freq)
