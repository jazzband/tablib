# -*- coding: utf-8 -*-

""" Tablib - ODF Support.
"""

import sys


if sys.version_info[0] > 2:
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO

from tablib.packages.odf.opendocument import OpenDocumentSpreadsheet
from tablib.packages.odf.style import Style, TextProperties, TableColumnProperties, Map
from tablib.packages.odf.number import NumberStyle, CurrencyStyle, CurrencySymbol,  Number,  Text
from tablib.packages.odf.text import P
from tablib.packages.odf.table import Table, TableColumn, TableRow, TableCell

from tablib.compat import unicode

title = 'ods'
extentions = ('ods',)

bold = Style(name='Bold', family="text")
bold.addElement(TextProperties(fontweight="bold"))

def export_set(dataset):
    """Returns ODF representation of Dataset."""

    wb = OpenDocumentSpreadsheet()
    wb.automaticstyles.addElement(bold)

    ws = Table(name=dataset.title if dataset.title else 'Tablib Dataset')
    wb.spreadsheet.addElement(ws)
    dset_sheet(dataset, ws)

    stream = BytesIO()
    wb.save(stream)
    return stream.getvalue()


def export_book(databook):
    """Returns ODF representation of DataBook."""

    wb = OpenDocumentSpreadsheet()
    wb.automaticstyles.addElement(bold)

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
        odf_row = TableRow(stylename=bold)
        for j, col in enumerate(row):
            ws.addElement(TableColumn())

            # bold headers
            if (row_number == 1) and dataset.headers:
                odf_row.setAttribute('stylename', bold)
                ws.addElement(odf_row)
                cell = TableCell()
                cell.addElement(P(stylename="Bold", text=unicode(col, errors='ignore')))
                odf_row.addElement(cell)

            # bold separators
            elif len(row) < dataset.width:
                ws.addElement(odf_row)
                cell = TableCell()
                cell.addElement(P(text=unicode(col, errors='ignore')))
                odf_row.addElement(cell)

            # wrap the rest
            else:
                try:
                    if '\n' in col:
                        ws.addElement(odf_row)
                        cell = TableCell()
                        cell.addElement(P(text=unicode(col, errors='ignore')))
                        odf_row.addElement(cell)
                    else:
                        ws.addElement(odf_row)
                        cell = TableCell()
                        cell.addElement(P(text=unicode(col, errors='ignore')))
                        odf_row.addElement(cell)
                except TypeError:
                    ws.addElement(odf_row)
                    cell = TableCell()
                    cell.addElement(P(text=unicode(col, errors='ignore')))
                    odf_row.addElement(cell)


