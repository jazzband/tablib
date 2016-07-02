# -*- coding: utf-8 -*-

""" Tablib - ODF Support.
"""

import sys


if sys.version_info[0] > 2:
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO


from tablib.packages import ods
from tablib.compat import unicode

title = 'ods'
extensions = ('ods',)


def export_set(dataset):
    """Returns ODF representation of Dataset."""

    stream = BytesIO()
    wb = ods.ODSWorkbook(stream)
    dset_sheet(dataset, wb, title='Sheet')
    wb.close()
    return stream.getvalue()


def export_book(databook):
    """Returns ODF representation of DataBook."""

    stream = BytesIO()
    wb = ods.ODSWorkbook(stream)

    for i, dataset in enumerate(databook._datasets):
        dset_sheet(dataset, wb, title='Sheet %d' % i)
    wb.close()
    return stream.getvalue()


def dset_sheet(dataset, wb, title=None):
    """Completes given worksheet from given Dataset."""
    _package = dataset._package(dicts=False)

    if not _package:
        return

    wb.start_sheet(len(_package[0]),
                   dataset.title if dataset.title else title)
    for i, sep in enumerate(dataset._separators):
        _offset = i
        _package.insert((sep[0] + _offset), (sep[1],))

    for i, row in enumerate(_package):
        cells = []
        for cell in row:
            try:
                cell = unicode(cell, errors='ignore')
            except TypeError:
                # col is already unicode
                pass
            cells.append(cell)
        if i == 0:
            wb.add_headers(cells)
        else:
            wb.add_row(cells)
    wb.end_sheet()
