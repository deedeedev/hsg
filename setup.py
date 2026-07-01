from setuptools import setup

setup(
    name='hsg',
    versio='0.1.0',
    py_modules=[
            'heisigtools',
            'heisigtatoeba',
            'ccedictsearch',
            'frequencytools',
        ],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'hsg = heisigtools:cli',
            'hsg-tatoeba = heisigtatoeba:cli',
            'hsg-cc = ccedictsearch:search',
            'hsg-freq = frequencytools:search',
        ],
    },
)