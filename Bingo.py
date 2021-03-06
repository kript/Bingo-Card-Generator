#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Originaly Taken from https://homework.nwsnet.de/releases/3822/
(Bullshit) Bingo Card Generator
===============================

**Bullshit Bingo** is a slight variation of `Buzzword Bingo`_.  The first player
completing a full row his/her card shouts "Bullshit!" to kindly inform the
presenter of a possible overuse of empty phrases.

Actually, this program is not restricted to this special type of Bingo.
Different kinds of words (and numbers, of course) can be used.

A word list (a plain text file with one term per word) is required as source
for the words that should be randomly used to create the bingo cards.

The randomly generated cards are put out as HTML and can be viewed and
printed with a common Web browser (e.g. Firefox_).

When generating multiple cards, two of them (with the default size) should fit
on one page of DIN A4 paper when printed.  Check your browser's printing
preview and, if necessary, adjust the CSS section of the HTML template.

Requires Python_ version 2.5 or greater, and Jinja2_ (tested with 2.6, earlier
versions may work). For a Python version before 2.7, the argparse_ module must
be installed separately.


Changelog
---------

- Switched template engine from Genshi to Jinja 2 to get more control over
  whitespace handling.

- Changed argument parser from optparse_ to argparse_.


.. _Buzzword Bingo: http://en.wikipedia.org/wiki/Buzzword_bingo
.. _Firefox:        http://www.mozilla.com/firefox/
.. _Python:         http://www.python.org/
.. _Jinja2:         http://jinja.pocoo.org/
.. _argparse:       http://code.google.com/p/argparse/
.. _optparse:       http://docs.python.org/library/optparse.html

:Copyright: 2007-2012 `Jochen Kupperschmidt <http://homework.nwsnet.de/>`_
: badly hacked around by John Constable 2020
:Date: 12-Jun-2012 (previous release: 09-Nov-2007)
:License: MIT
"""

from __future__ import with_statement
import argparse
import codecs
from collections import namedtuple
from itertools import chain, islice, zip_longest, repeat
from random import randrange, sample
import sys

import jinja2


Field = namedtuple('Field', ['type', 'value'])

FIELD_EMPTY = Field('empty', None)
FIELD_BONUS = Field('bonus', None)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument('words_file',
        metavar='<words file>')

    parser.add_argument('-b', '--bonus-field',
        dest='include_bonus_field',
        action='store_true',
        default=False,
        help='add one bonus field per card')

    parser.add_argument('-c', '--num-cards',
        dest='num_cards',
        type=int,
        default=1,
        help='number of cards to create (default: 1)')

    parser.add_argument('-s', '--card-size',
        dest='card_size',
        type=int,
        default=5,
        help='number of rows and columns per card (default: 5)')

    return parser.parse_args()

def load_words(filename):
    """Load words from a file.

    Every line is to be considered as one word.
    """
    #with codecs.open(filename, 'rb') as f:
    with codecs.open(filename, 'r') as f:
        for line in f:
            # Only yield non-empty, non-whitespace lines.
            line = line.strip()
            if line:
                yield line

def build_table(values, size, include_bonus_field=False):
    """Build a 2-dimensional table of the given size with unique, random
    values.

    If the table has more fields than values are available, the remaining
    fields will be empty.
    """
    field_total = size ** 2
    random_values = collect_random_sublist(values, field_total)
    fields = to_fields(random_values, field_total)

    if include_bonus_field:
        # Replace a field at a random position with a bonus field.
        fields[randrange(0, field_total)] = FIELD_BONUS

    # Group into rows.
    return zip_longest(*[iter(fields)] * size)

def collect_random_sublist(values, n):
    """Return unique, random elements from the values.

    Return `n` values or, if `n` is greater than the number of values, all
    values.
    """
    # The sample length must not exceed the number of available values.
    sample_length = min(n, len(values))
    return sample(values, sample_length)

def to_fields(values, n):
    """Create fields from the values, append infinite empty fields, and return
    the first `n` items.
    """
    normal_fields = (Field('normal', value) for value in values)
    fields = chain(normal_fields, repeat(FIELD_EMPTY))
    return take(fields, n)

def take(iterable, n):
    """Return the first `n` items of the iterable as a list."""
    return list(islice(iterable, n))

def render_html(tables):
    """Assemble an HTML page with cards from the word tables."""
    #env = Environment(autoescape=True)
    #template = env.from_string(TEMPLATE)
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader, autoescape=True)
    TEMPLATE_FILE = "template.html"
    template = templateEnv.get_template(TEMPLATE_FILE)
    return template.render(tables=tables)

if __name__ == '__main__':
    args = parse_args()

    # Load words from given file.
    words = frozenset(load_words(args.words_file))

    # Create tables of words.
    tables = [list(build_table(words, args.card_size, args.include_bonus_field))
        for _ in range(args.num_cards)]

    # Write HTML output to stdout.  To create a file, redirect the data by
    # appending something like ``> cards.html`` at the command line.
    #html = render_html(tables).encode('utf-8')
    html = render_html(tables).encode()
    #print(html)
    with open("Bingo.html", "wb") as fh:
      fh.write(html)
