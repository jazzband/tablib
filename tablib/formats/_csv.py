# -*- coding: utf-8 -*-

""" Tablib - CSV Support.
"""

from tablib.compat import is_py3, csv, StringIO


title = 'csv'
extensions = ('csv',)


DEFAULT_ENCODING = 'utf-8'



def export_set(dataset, **kwargs):
    """Returns CSV representation of Dataset."""
    stream = StringIO()

    if not is_py3:
        kwargs.setdefault('encoding', DEFAULT_ENCODING)

    _csv = csv.writer(stream, **kwargs)

    for row in dataset._package(dicts=False):
        _csv.writerow(row)

    return stream.getvalue()


def import_set(dset, in_stream, headers=True, **kwargs):
    """Returns dataset from CSV stream."""

    dset.wipe()

    if not is_py3:
        kwargs.setdefault('encoding', DEFAULT_ENCODING)

    rows = csv.reader(StringIO(in_stream), **kwargs)
    for i, row in enumerate(rows):

        if (i == 0) and (headers):
            dset.headers = row
        else:
            dset.append(row)


def detect(stream):
    """Returns True if given stream is valid CSV."""
    try:
        csv.Sniffer().sniff(stream, delimiters=',')
        return True
    except (csv.Error, TypeError):
        return False
