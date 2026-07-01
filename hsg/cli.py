import click

from hsg.commands.heisigtools import stories, parse, enrich
from hsg.commands.heisigtools import list as list_cmd
from hsg.commands.heisigtatoeba import sentences, random_sentences
from hsg.commands.ccedictsearch import search as lookup
from hsg.commands.frequencytools import search as freq


@click.group()
def cli():
    pass


cli.add_command(parse)
cli.add_command(enrich)
cli.add_command(list_cmd)
cli.add_command(stories)
cli.add_command(sentences)
cli.add_command(random_sentences)
cli.add_command(lookup)
cli.add_command(freq)
