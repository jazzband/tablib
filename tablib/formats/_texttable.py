# -*- coding: utf-8 -*-

""" Text Table Support.
"""

title = 'texttable'
extentions = ('texttable',)

DEFAULT_ENCODING = 'utf-8'

import tablib.packages.texttable as texttable  # so clients can use constants like Texttable.HEADER

def export_set(dataset):
    """Returns a texttable representation of Dataset."""

    global deco

    table = texttable.Texttable()

    if 'deco' in globals():
        table.set_deco(deco)

    first_row = True

    for row in dataset._package(dicts=False):
        if first_row:
            table.header(row)
            first_row = False
        else:
            table.add_row(row)

    return table.draw()
