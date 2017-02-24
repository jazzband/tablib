# -*- coding: utf-8 -*-

""" Tablib - JSON Support
"""
import decimal

import tablib

try:
    import ujson as json
except ImportError:
    import json

title = 'json'
extensions = ('json', 'jsn')


def date_handler(obj):
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        return obj
    # return obj.isoformat() if hasattr(obj, 'isoformat') else obj


def export_set(dataset):
    """Returns JSON representation of Dataset."""
    return json.dumps(dataset.dict, default=date_handler)


def export_book(databook):
    """Returns JSON representation of Databook."""
    return json.dumps(databook._package(), default=date_handler)


def import_set(dset, in_stream):
    """Returns dataset from JSON stream."""

    dset.wipe()
    dset.dict = json.loads(in_stream)


def import_book(dbook, in_stream):
    """Returns databook from JSON stream."""

    dbook.wipe()
    for sheet in json.loads(in_stream):
        data = tablib.Dataset()
        data.title = sheet['title']
        data.dict = sheet['data']
        dbook.add_sheet(data)


def detect(stream):
    """Returns True if given stream is valid JSON."""
    try:
        json.loads(stream)
        return True
    except ValueError:
        return False
