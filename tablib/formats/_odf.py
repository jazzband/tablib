# -*- coding: utf-8 -*-

""" Tablib - ODF Support.
"""

import sys


if sys.version_info[0] > 2:
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO

from tablib.compat import openpyxl

from odf.opendocument import OpenDocumentSpreadsheet
from odf.style import Style, TextProperties, TableColumnProperties, Map
from odf.number import NumberStyle, CurrencyStyle, CurrencySymbol,  Number,  Text
from odf.text import P
from odf.table import Table, TableColumn, TableRow, TableCell

from tablib.compat import unicode

title = 'odf'
extentions = ('odf',)

def export_set(dataset):
    """Returns ODF representation of Dataset."""

    wb = OpenDocumentSpreadsheet()
    ws = Table(name=dataset.title if dataset.title else 'Tablib Dataset')
    wb.spreadsheet.addElement(ws)
    dset_sheet(dataset, ws)

    stream = BytesIO()
    wb.save(stream)
    return stream.getvalue()


def export_book(databook):
    """Returns ODF representation of DataBook."""

    wb = OpenDocumentSpreadsheet()
    for i, dset in enumerate(databook._datasets):
        ws = Table(name=dset.title if dset.title else 'Sheet%s' % (i))
        wb.spreadsheet.addElement(ws)
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
        row_number = i + 1
        odf_row = TableRow()
        for j, col in enumerate(row):
            ws.addElement(TableColumn())
            #col_idx = get_column_letter(j + 1)

            # bold headers
            if (row_number == 1) and dataset.headers:
                ws.addElement(odf_row)
                cell = TableCell()
                cell.addElement(P(text=col))
                odf_row.addElement(cell)
                #style = ws.get_style('%s%s' % (col_idx, row_number))
                #style.font.bold = True
                #ws.freeze_panes = '%s%s' % (col_idx, row_number)


            # bold separators
            elif len(row) < dataset.width:
                ws.addElement(odf_row)
                cell = TableCell()
                cell.addElement(P(text=col))
                odf_row.addElement(cell)
                #ws.cell('%s%s'%(col_idx, row_number)).value = unicode(
                #    '%s' % col, errors='ignore')
                #style = ws.get_style('%s%s' % (col_idx, row_number))
                #style.font.bold = True

            # wrap the rest
            else:
                try:
                    if '\n' in col:
                        ws.addElement(odf_row)
                        cell = TableCell()
                        cell.addElement(P(text=col))
                        odf_row.addElement(cell)
                        #ws.cell('%s%s'%(col_idx, row_number)).value = unicode(
                        #    '%s' % col, errors='ignore')
                        #style = ws.get_style('%s%s' % (col_idx, row_number))
                        #style.alignment.wrap_text
                    else:
                        ws.addElement(odf_row)
                        cell = TableCell()
                        cell.addElement(P(text=col))
                        odf_row.addElement(cell)
                        #ws.cell('%s%s'%(col_idx, row_number)).value = unicode(
                        #    '%s' % col, errors='ignore')
                except TypeError:
                    ws.addElement(odf_row)
                    cell = TableCell()
                    cell.addElement(P(text=col))
                    odf_row.addElement(cell)
                    #ws.cell('%s%s'%(col_idx, row_number)).value = unicode(col)


