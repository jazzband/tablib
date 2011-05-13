# -*- coding: utf-8 -*-

""" Tablib - XLSX Support.
"""

import sys


if sys.version_info[0] > 2:
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO

from tablib.compat import openpyxl

Workbook = openpyxl.workbook.Workbook
ExcelWriter = openpyxl.writer.excel.ExcelWriter
get_column_letter = openpyxl.cell.get_column_letter

from tablib.compat import unicode


title = 'xlsx'
extentions = ('xlsx',)

def export_set(dataset):
    """Returns XLSX representation of Dataset."""

    wb = Workbook()
    ws = wb.worksheets[0]
    ws.title = dataset.title if dataset.title else 'Tablib Dataset'

    dset_sheet(dataset, ws)

    stream = BytesIO()
    wb.save(stream)
    return stream.getvalue()


def export_book(databook):
    """Returns XLSX representation of DataBook."""

    wb = Workbook()
    ew = ExcelWriter(workbook = wb)
    for i, dset in enumerate(databook._datasets):
        ws = wb.create_sheet()
        ws.title = dset.title if dset.title else 'Sheet%s' % (i)

        dset_sheet(dset, ws)


    stream = BytesIO()
    ew.save(stream)
    return stream.getvalue()


def dset_sheet(dataset, ws):
    """Completes given worksheet from given Dataset."""
    _package = dataset._package(dicts=False)

    for i, sep in enumerate(dataset._separators):
        _offset = i
        _package.insert((sep[0] + _offset), (sep[1],))

    for i, row in enumerate(_package):
        row_number = i + 1
        for j, col in enumerate(row):
            col_idx = get_column_letter(j + 1)

            # bold headers
            if (row_number == 1) and dataset.headers:
                # ws.cell('%s%s'%(col_idx, row_number)).value = unicode(
                    # '%s' % col, errors='ignore')
                ws.cell('%s%s'%(col_idx, row_number)).value = unicode(col)
                style = ws.get_style('%s%s' % (col_idx, row_number))
                style.font.bold = True
                ws.freeze_panes = '%s%s' % (col_idx, row_number)


            # bold separators
            elif len(row) < dataset.width:
                ws.cell('%s%s'%(col_idx, row_number)).value = unicode(
                    '%s' % col, errors='ignore')
                style = ws.get_style('%s%s' % (col_idx, row_number))
                style.font.bold = True

            # wrap the rest
            else:
                try:
                    if '\n' in col:
                        ws.cell('%s%s'%(col_idx, row_number)).value = unicode(
                            '%s' % col, errors='ignore')
                        style = ws.get_style('%s%s' % (col_idx, row_number))
                        style.alignment.wrap_text
                    else:
                        ws.cell('%s%s'%(col_idx, row_number)).value = unicode(
                            '%s' % col, errors='ignore')
                except TypeError:
                    ws.cell('%s%s'%(col_idx, row_number)).value = unicode(col)


