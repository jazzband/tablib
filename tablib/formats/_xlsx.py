# -*- coding: utf-8 -*-

""" Tablib - XLSX Support.
"""

import sys


if sys.version_info[0] > 2:
    from io import BytesIO
    import tablib.packages.xlwt3 as xlwt
    
else:
    from cStringIO import StringIO as BytesIO
    import tablib.packages.xlwt as xlwt

from tablib.packages.openpyxl.workbook import Workbook
from tablib.packages.openpyxl.writer.excel import ExcelWriter

from tablib.packages.openpyxl.cell import get_column_letter    



title = 'xlsx'
extentions = ('xlsx',)

# special styles
#wrap = xlwt.easyxf("alignment: wrap on")
#bold = xlwt.easyxf("font: bold on")


def export_set(dataset):
    """Returns XLS representation of Dataset."""

    wb = Workbook()
    ws = wb.worksheets[0]
    ws.title = dataset.title if dataset.title else 'Tablib Dataset'

    dset_sheet(dataset, ws)

    stream = BytesIO()
    wb.save(stream)
    return stream.getvalue()


def export_book(databook):
    """Returns XLS representation of DataBook."""

    wb = Workbook()
    ew = ExcelWriter(workbook = wb)
    for i, dset in enumerate(databook._datasets):
        ws = wb.add_sheet()
        ws.title = dset.title if dset.title else 'Sheet%s' % (i)

        dset_sheet(dset, ws)


    stream = BytesIO()
    ew.save(filename='test.xlsx')
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
                ws.cell('%s%s'%(col_idx, row_number)).value = '%s' % col
                #ws.write(i, j, col, bold)

                # frozen header row
                #ws.panes_frozen = True
                #ws.horz_split_pos = 1


            # bold separators
            elif len(row) < dataset.width:
                ws.cell('%s%s'%(col_idx, row_number)).value = '%s' % col
                #ws.write(i, j, col, bold)

            # wrap the rest
            else:
                try:
                    if '\n' in col:
                        ws.cell('%s%s'%(col_idx, row_number)).value = '%s' % col
                        #ws.write(i, j, col, wrap)
                    else:
                        ws.cell('%s%s'%(col_idx, row_number)).value = '%s' % col
                        #ws.write(i, j, col)
                except TypeError:
                    ws.cell('%s%s'%(col_idx, row_number)).value = '%s' % col
                    #ws.write(i, j, col)


