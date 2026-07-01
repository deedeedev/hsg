from setuptools import setup

setup(
    name='hsg',
    version='0.1.0',
    packages=['hsg', 'hsg.commands', 'hsg.classes', 'hsg.utils'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'hsg = hsg.commands.heisigtools:cli',
            'hsg-tatoeba = hsg.commands.heisigtatoeba:cli',
            'hsg-cc = hsg.commands.ccedictsearch:search',
            'hsg-freq = hsg.commands.frequencytools:search',
        ],
    },
)