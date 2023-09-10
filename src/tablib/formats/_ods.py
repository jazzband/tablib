""" Tablib - ODF Support.
"""

import datetime as dt
import numbers
from io import BytesIO

from odf import opendocument, style, table, text

import tablib

bold = style.Style(name="bold", family="paragraph")
bold.addElement(style.TextProperties(
    fontweight="bold",
    fontweightasian="bold",
    fontweightcomplex="bold",
))


class ODSFormat:
    title = 'ods'
    extensions = ('ods',)

    @classmethod
    def export_set(cls, dataset):
        """Returns ODF representation of Dataset."""

        wb = opendocument.OpenDocumentSpreadsheet()
        wb.automaticstyles.addElement(bold)

        ws = table.Table(name=dataset.title if dataset.title else 'Tablib Dataset')
        wb.spreadsheet.addElement(ws)
        cls.dset_sheet(dataset, ws)

        stream = BytesIO()
        wb.save(stream)
        return stream.getvalue()

    @classmethod
    def export_book(cls, databook):
        """Returns ODF representation of DataBook."""

        wb = opendocument.OpenDocumentSpreadsheet()
        wb.automaticstyles.addElement(bold)

        for i, dset in enumerate(databook._datasets):
            ws = table.Table(name=dset.title if dset.title else f"Sheet{i}")
            wb.spreadsheet.addElement(ws)
            cls.dset_sheet(dset, ws)

        stream = BytesIO()
        wb.save(stream)
        return stream.getvalue()

    @classmethod
    def import_sheet(cls, dset, sheet, headers=True, skip_lines=0):
        """Populate dataset `dset` with sheet data."""

        dset.title = sheet.getAttribute('name')

        def is_real_cell(cell):
            return cell.hasChildNodes() or not cell.getAttribute('numbercolumnsrepeated')

        for i, row in enumerate(sheet.childNodes):
            if row.tagName != 'table:table-row':
                continue
            if i < skip_lines:
                continue
            row_vals = [cls.read_cell(cell) for cell in row.childNodes if is_real_cell(cell)]
            if not row_vals:
                continue
            if i == skip_lines and headers:
                dset.headers = row_vals
            else:
                if i > skip_lines and len(row_vals) < dset.width:
                    row_vals += [''] * (dset.width - len(row_vals))
                dset.append(row_vals)

    @classmethod
    def read_cell(cls, cell, value_type=None):
        def convert_date(val):
            if 'T' in val:
                return dt.datetime.strptime(val, "%Y-%m-%dT%H:%M:%S")
            else:
                return dt.datetime.strptime(val, "%Y-%m-%d").date()

        if value_type is None:
            value_type = cell.getAttribute('valuetype')
        if value_type == 'date':
            date_value = cell.getAttribute('datevalue')
            if date_value:
                return convert_date(date_value)
        if value_type == 'time':
            time_value = cell.getAttribute('timevalue')
            return dt.datetime.strptime(time_value, "%H:%M:%S").time()
        if value_type == 'boolean':
            bool_value = cell.getAttribute('booleanvalue')
            return bool_value == 'true'
        if not cell.childNodes:
            value = getattr(cell, 'data', None)
            if value is None:
                value = cell.getAttribute('value')
            if value is None:
                return ''
            if value_type == 'float':
                return float(value)
            if value_type == 'date':
                return convert_date(value)
            return value  # Any other type default to 'string'

        for subnode in cell.childNodes:
            value = cls.read_cell(subnode, value_type)
            if value:
                return value

    @classmethod
    def import_set(cls, dset, in_stream, headers=True, skip_lines=0):
        """Populate dataset `dset` from ODS stream."""

        dset.wipe()

        ods_book = opendocument.load(in_stream)
        for sheet in ods_book.spreadsheet.childNodes:
            if sheet.qname[1] == 'table':
                cls.import_sheet(dset, sheet, headers, skip_lines)

    @classmethod
    def import_book(cls, dbook, in_stream, headers=True):
        """Populate databook `dbook` from ODS stream."""

        dbook.wipe()

        ods_book = opendocument.load(in_stream)

        for sheet in ods_book.spreadsheet.childNodes:
            if sheet.qname[1] != 'table':
                continue
            dset = tablib.Dataset()
            cls.import_sheet(dset, sheet, headers)
            dbook.add_sheet(dset)

    @classmethod
    def dset_sheet(cls, dataset, ws):
        """Completes given worksheet from given Dataset."""
        _package = dataset._package(dicts=False)

        for i, sep in enumerate(dataset._separators):
            _offset = i
            _package.insert((sep[0] + _offset), (sep[1],))

        for row_number, row in enumerate(_package, start=1):
            is_header = row_number == 1 and dataset.headers
            style = bold if is_header else None
            odf_row = table.TableRow(stylename=style)
            ws.addElement(odf_row)
            for j, col in enumerate(row):
                if isinstance(col, numbers.Number):
                    cell = table.TableCell(valuetype="float", value=col)
                elif isinstance(col, dt.datetime):
                    cell = table.TableCell(
                        valuetype="date", value=col.strftime('%Y-%m-%dT%H:%M:%S')
                    )
                elif isinstance(col, dt.date):
                    cell = table.TableCell(valuetype="date", datevalue=col.strftime('%Y-%m-%d'))
                elif isinstance(col, dt.time):
                    cell = table.TableCell(valuetype="time", timevalue=col.strftime('%H:%M:%S'))
                elif col is None:
                    cell = table.TableCell(valuetype="void")
                else:
                    cell = table.TableCell(valuetype="string")
                    cell.addElement(text.P(text=str(col), stylename=style))
                odf_row.addElement(cell)

    @classmethod
    def detect(cls, stream):
        if isinstance(stream, bytes):
            # load expects a file-like object.
            stream = BytesIO(stream)
        try:
            opendocument.load(stream)
            return True
        except Exception:
            return False
