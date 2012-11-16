# -*- coding: utf-8 -*-

""" Tablib - TSV (Tab Separated Values) Support.
"""

from tablib.compat import is_py3, csv, StringIO



title = 'tsv'
extensions = ('tsv',)

DEFAULT_ENCODING = 'utf-8'

def export_set(dataset):
    """Returns a TSV representation of Dataset."""

    stream = StringIO()

    if is_py3:
        _tsv = csv.writer(stream, delimiter='\t')
    else:
        _tsv = csv.writer(stream, encoding=DEFAULT_ENCODING, delimiter='\t')

    for row in dataset._package(dicts=False):
        _tsv.writerow(row)

    return stream.getvalue()


def import_set(dset, in_stream, headers=True):
    """Returns dataset from TSV stream."""

    dset.wipe()

    if is_py3:
        rows = csv.reader(in_stream.splitlines(), delimiter='\t')
    else:
        rows = csv.reader(in_stream.splitlines(), delimiter='\t',
                          encoding=DEFAULT_ENCODING)

    for i, row in enumerate(rows):
        # Skip empty rows
        if not row:
            continue

        if (i == 0) and (headers):
            dset.headers = row
        else:
            dset.append(row)


def detect(stream):
    """Returns True if given stream is valid TSV."""
    try:
        csv.Sniffer().sniff(stream, delimiters='\t')
        return True
    except (csv.Error, TypeError):
        return False
