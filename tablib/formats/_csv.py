# -*- coding: utf-8 -*-

""" Tablib - CSV Support.
"""

from tablib.compat import is_py3, csv, StringIO


title = 'csv'
extensions = ('csv',)


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

    # get width of widest row
    lines = in_stream.splitlines()
    reader = csv.reader(lines)
    max_width = max(len(row) for row in reader)
    del lines, reader

    if is_py3:
        rows = csv.reader(StringIO(in_stream))
    else:
        rows = csv.reader(StringIO(in_stream), encoding=DEFAULT_ENCODING)

    for i, row in enumerate(rows):
        # fill in empty cells to make all rows match the width of the widest row
        row.extend([''] * (max_width - len(row)))

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
