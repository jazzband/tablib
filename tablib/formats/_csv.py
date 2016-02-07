# -*- coding: utf-8 -*-

""" Tablib - *SV Support.
"""

from tablib.compat import is_py3, csv, StringIO


title = 'csv'
extensions = ('csv',)


DEFAULT_ENCODING = 'utf-8'
DEFAULT_DELIMITER = ','


def export_set(dataset, delimiter=DEFAULT_DELIMITER):
    """Returns CSV representation of Dataset."""
    stream = StringIO()

    if is_py3:
        _csv = csv.writer(stream, delimiter=delimiter)
    else:
        _csv = csv.writer(stream, delimiter=delimiter, encoding=DEFAULT_ENCODING)

    for row in dataset._package(dicts=False):
        _csv.writerow(row)

    return stream.getvalue()


def import_set(dset, in_stream, headers=True, delimiter=DEFAULT_DELIMITER):
    """Returns dataset from CSV stream."""

    dset.wipe()

    if is_py3:
        rows = csv.reader(StringIO(in_stream), delimiter=delimiter)
    else:
        rows = csv.reader(StringIO(in_stream), delimiter=delimiter, encoding=DEFAULT_ENCODING)
    for i, row in enumerate(rows):

        if (i == 0) and (headers):
            dset.headers = row
        else:
            dset.append(row)


def detect(stream, delimiter=DEFAULT_DELIMITER):
    """Returns True if given stream is valid CSV."""
    try:
        csv.Sniffer().sniff(stream, delimiters=delimiter)
        return True
    except (csv.Error, TypeError):
        return False
