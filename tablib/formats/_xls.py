# -*- coding: utf-8 -*-

""" Tablib - XLS Support.
"""

import sys

from tablib.compat import BytesIO, xlwt, xlrd
import tablib

title = 'xls'
extentions = ('xls',)

# special styles
wrap = xlwt.easyxf("alignment: wrap on")
bold = xlwt.easyxf("font: bold on")


def import_set(dset, in_stream, headers=True):
    """Returns dataset from XLS stream."""

    dset.wipe()
    
    wb = xlrd.open_workbook(file_contents=in_stream)
    ws = wb.sheet_by_index(0)
    
    for i in range(ws.nrows):
        if (i == 0) and (headers):
            dset.headers = ws.row_values(i)
        else:
            dset.append(ws.row_values(i))

            
def import_book(dbook, in_stream, headers=True):
    """Returns databook from XLS stream."""

    dbook.wipe()
    
    wb = xlrd.open_workbook(file_contents=in_stream)
    for ws in wb.sheets():
        data = tablib.Dataset()
        data.title = ws.name
        for i in range(ws.nrows):
            if (i == 0) and (headers):
                data.headers = ws.row_values(i)
            else:
                data.append(ws.row_values(i))
        dbook.add_sheet(data)


def export_set(dataset):
    """Returns XLS representation of Dataset."""

    wb = xlwt.Workbook(encoding='utf8')
    ws = wb.add_sheet(dataset.title if dataset.title else 'Tablib Dataset')

    dset_sheet(dataset, ws)

    stream = BytesIO()
    wb.save(stream)
    return stream.getvalue()


def export_book(databook):
    """Returns XLS representation of DataBook."""

    wb = xlwt.Workbook(encoding='utf8')

    for i, dset in enumerate(databook._datasets):
        ws = wb.add_sheet(dset.title if dset.title else 'Sheet%s' % (i))

        dset_sheet(dset, ws)


    stream = BytesIO()
    wb.save(stream)
    return stream.getvalue()


def dset_sheet(dataset, ws):
    """Completes given worksheet from given Dataset."""
    _package = dataset._package(dicts=False)

    for i, sep in enumerate(dataset._separators):
        _offset = i
        _package.insert((sep[0] + _offset), (sep[1],))

    for i, row in enumerate(_package):
        for j, col in enumerate(row):

            # bold headers
            if (i == 0) and dataset.headers:
                ws.write(i, j, col, bold)

                # frozen header row
                ws.panes_frozen = True
                ws.horz_split_pos = 1


            # bold separators
            elif len(row) < dataset.width:
                ws.write(i, j, col, bold)

            # wrap the rest
            else:
                try:
                    if '\n' in col:
                        ws.write(i, j, col, wrap)
                    else:
                        ws.write(i, j, col)
                except TypeError:
                    ws.write(i, j, col)


def detect(stream):
    """Returns True if given stream is valid XLS."""
    
    try:
        xlrd.open_workbook(file_contents=stream)
        return True
    except xlrd.XLRDError:
        return False
