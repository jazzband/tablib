# -*- coding: utf-8 -*-

""" Tablib - TSV (Tab Separated Values) Support.
"""

from tablib.compat import unicode
from tablib.formats._csv import (
    export_set as export_set_wrapper,
    import_set as import_set_wrapper,
    detect as detect_wrapper,
)

title = 'tsv'
extensions = ('tsv',)

DELIMITER = unicode('\t')

def export_set(dataset):
    """Returns TSV representation of Dataset."""
    return export_set_wrapper(dataset, delimiter=DELIMITER)


def import_set(dset, in_stream, headers=True):
    """Returns dataset from TSV stream."""
    return import_set_wrapper(dset, in_stream, headers=headers, delimiter=DELIMITER)


def detect(stream):
    """Returns True if given stream is valid TSV."""
    return detect_wrapper(stream, delimiter=DELIMITER)
