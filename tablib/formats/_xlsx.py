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

def set_value(cell, addr, value):
    """ assign a value, taking care to identify numeric-looking strings """
    
    cell(addr).set_value_explicit(value)
    #if value[0] == '0':
    #    cell(addr).set_value_explicit(value)
    #else:
    #    cell(addr).value = unicode(value, errors='ignore')
    
    return cell

def dset_sheet(dataset, ws):
    """Completes given worksheet from given Dataset."""
    _package = dataset._package(dicts=False)

    for i, sep in enumerate(dataset._separators):
        _offset = i
        _package.insert((sep[0] + _offset), (sep[1],))
    import pdb
    for i, row in enumerate(_package):
        row_number = i + 1
        for j, col in enumerate(row):
            col_idx = get_column_letter(j + 1)
            addr = '%s%s'%(col_idx, row_number)
            value = '%s' % col
            #if '2169' in value:
            #    pdb.set_trace()
            # bold headers
            if (row_number == 1) and dataset.headers:
                ws.cell(addr).value = unicode(col)
                style = ws.get_style(addr)
                style.font.bold = True
                ws.freeze_panes = addr

            # bold separators
            elif len(row) < dataset.width:
                ws.cell = set_value(ws.cell, addr, value)
                style = ws.get_style(addr)
                style.font.bold = True

            # wrap the rest
            else:
                try:
                    ws.cell = set_value(ws.cell, addr, value)
                    if '\n' in col:
                        style = ws.get_style(addr)
                        style.alignment.wrap_text
                except TypeError:
                    ws.cell = set_value(ws.cell, addr, value)


