# -*- coding: utf-8 -*-

""" Tablib - JSON Support
"""

import tablib

import sys
if sys.version_info[:2] > (2, 5):
    from tablib.packages import anyjson
else:
    from tablib.packages import anyjson25 as anyjson



title = 'json'
extentions = ('json', 'jsn')


def export_set(dataset):
    """Returns JSON representation of Dataset."""
    return anyjson.serialize(dataset.dict)


def export_book(databook):
    """Returns JSON representation of Databook."""
    return anyjson.serialize(databook._package())


def import_set(dset, in_stream):
    """Returns dataset from JSON stream."""

    dset.wipe()
    dset.dict = anyjson.deserialize(in_stream)


def import_book(dbook, in_stream):
    """Returns databook from JSON stream."""

    dbook.wipe()
    for sheet in anyjson.deserialize(in_stream):
        data = tablib.Dataset()
        data.title = sheet['title']
        data.dict = sheet['data']
        dbook.add_sheet(data)


def detect(stream):
    """Returns True if given stream is valid JSON."""
    try:
        anyjson.deserialize(stream)
        return True
    except ValueError:
        return False
