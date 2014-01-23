# -*- coding: utf-8 -*-

""" Tablib - Fixed Width Support.
"""

from struct import Struct


title = 'fix'
extensions = ('fix',)


DEFAULT_ENCODING = 'utf-8'


def check_fields_width(dset):
    if not hasattr(dset, 'fields_width'):
        raise Exception('You have to define fields_width to Dataset')


def export_set(dataset):
    lines = []
    for idx, row in enumerate(dataset._package(dicts=False)):
        if dataset.headers and idx == 0:
            continue
        lines.append(
            ''.join([str(x).ljust(y)
                     for x, y in zip(row, dataset.fields_width)])
        )
    return '\n'.join(lines)


def import_set(dset, in_stream, headers=True):
    """Returns dataset from CSV stream."""

    fixed_struct = Struct(dset.fields_width)
    for row in in_stream.splitlines():
        dset.extend([fixed_struct.unpack(row)])
