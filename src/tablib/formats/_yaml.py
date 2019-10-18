# -*- coding: utf-8 -*-

""" Tablib - YAML Support.
"""

import tablib
import yaml

title = 'yaml'
extensions = ('yaml', 'yml')


def export_set(dataset):
    """Returns YAML representation of Dataset."""

    return yaml.safe_dump(dataset._package(ordered=False))


def export_book(databook):
    """Returns YAML representation of Databook."""
    return yaml.safe_dump(databook._package(ordered=False))


def import_set(dset, in_stream):
    """Returns dataset from YAML stream."""

    dset.wipe()
    dset.dict = yaml.safe_load(in_stream)


def import_book(dbook, in_stream):
    """Returns databook from YAML stream."""

    dbook.wipe()

    for sheet in yaml.safe_load(in_stream):
        data = tablib.Dataset()
        data.title = sheet['title']
        data.dict = sheet['data']
        dbook.add_sheet(data)


def detect(stream):
    """Returns True if given stream is valid YAML."""
    try:
        _yaml = yaml.safe_load(stream)
        if isinstance(_yaml, (list, tuple, dict)):
            return True
        else:
            return False
    except (yaml.parser.ParserError, yaml.reader.ReaderError,
            yaml.scanner.ScannerError):
        return False
