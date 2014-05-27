# -*- coding: utf-8 -*-

""" Tablib - XLSX Support.
"""

import sys


if sys.version_info[0] > 2:
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO

from tablib.compat import openpyxl
import tablib

Workbook = openpyxl.workbook.Workbook
ExcelWriter = openpyxl.writer.excel.ExcelWriter
get_column_letter = openpyxl.cell.get_column_letter

from tablib.compat import unicode


title = 'xlsx'
extensions = ('xlsx',)


def detect(stream):
    """Returns True if given stream is a readable excel file."""
    try:
        openpyxl.reader.excel.load_workbook(stream)
        return True
    except openpyxl.shared.exc.InvalidFileException:
        pass

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
    wb.worksheets = []
    for i, dset in enumerate(databook._datasets):
        ws = wb.create_sheet()
        ws.title = dset.title if dset.title else 'Sheet%s' % (i)

        dset_sheet(dset, ws)


    stream = BytesIO()
    wb.save(stream)
    return stream.getvalue()


def import_set(dset, in_stream, headers=True):
    """Returns databook from XLS stream."""

    dset.wipe()

    xls_book = openpyxl.reader.excel.load_workbook(in_stream)
    sheet = xls_book.get_active_sheet()

    dset.title = sheet.title

    for i, row in enumerate(sheet.rows):
        row_vals = [c.value for c in row]
        if (i == 0) and (headers):
            dset.headers = row_vals
        else:
            dset.append(row_vals)


def import_book(dbook, in_stream, headers=True):
    """Returns databook from XLS stream."""

    dbook.wipe()

    xls_book = openpyxl.reader.excel.load_workbook(in_stream)

    for sheet in xls_book.worksheets:
        data = tablib.Dataset()
        data.title = sheet.title

        for i, row in enumerate(sheet.rows):
            row_vals = [c.value for c in row]
            if (i == 0) and (headers):
                data.headers = row_vals
            else:
                data.append(row_vals)

        dbook.add_sheet(data)


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
            # We want to freeze the column after the last column
            frzn_col_idx = get_column_letter(j + 2)

            # bold headers
            if (row_number == 1) and dataset.headers:
                # ws.cell('%s%s'%(col_idx, row_number)).value = unicode(
                    # '%s' % col, errors='ignore')
                ws.cell('%s%s'%(col_idx, row_number)).value = unicode(col)
                style = ws.get_style('%s%s' % (col_idx, row_number))
                style.font.bold = True
                ws.freeze_panes = '%s%s' % (frzn_col_idx, row_number)


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


