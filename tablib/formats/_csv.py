# -*- coding: utf-8 -*-

""" Tablib - CSV Support.
"""

from tablib.compat import is_py3, csv, StringIO


title = 'csv'
extentions = ('csv',)


DEFAULT_ENCODING = 'utf-8'



def export_set(dataset):
    """Returns CSV representation of Dataset."""
    stream = StringIO()

    if is_py3:
        _csv = csv.writer(stream)
    else:
        _csv = csv.writer(stream, encoding=DEFAULT_ENCODING)

    for row in dataset._package(dicts=False):
        _csv.writerow(row)

    return stream.getvalue()


def import_set(dset, in_stream, headers=True):
    """Returns dataset from CSV stream."""

    dset.wipe()

    if is_py3:
        rows = csv.reader(in_stream.splitlines())
    else:
        rows = csv.reader(in_stream.splitlines(), encoding=DEFAULT_ENCODING)
    for i, row in enumerate(rows):

        if (i == 0) and (headers):
            dset.headers = row
        else:
            dset.append(row)


def detect(stream):
    """Returns True if given stream is valid CSV."""
    try:
        csv.Sniffer().sniff(stream)
        return True
    except csv.Error:
        return False