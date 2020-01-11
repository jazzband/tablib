""" Tablib - XLS Support.
"""

from io import BytesIO

import tablib
import xlrd
import xlwt

# special styles
wrap = xlwt.easyxf("alignment: wrap on")
bold = xlwt.easyxf("font: bold on")


class XLSFormat:
    title = 'xls'
    extensions = ('xls',)

    @classmethod
    def detect(cls, stream):
        """Returns True if given stream is a readable excel file."""
        try:
            xlrd.open_workbook(file_contents=stream)
            return True
        except Exception:
            pass
        try:
            xlrd.open_workbook(file_contents=stream.read())
            return True
        except Exception:
            pass
        try:
            xlrd.open_workbook(filename=stream)
            return True
        except Exception:
            return False

    @classmethod
    def export_set(cls, dataset):
        """Returns XLS representation of Dataset."""

        wb = xlwt.Workbook(encoding='utf8')
        ws = wb.add_sheet(dataset.title if dataset.title else 'Tablib Dataset')

        cls.dset_sheet(dataset, ws)

        stream = BytesIO()
        wb.save(stream)
        return stream.getvalue()

    @classmethod
    def export_book(cls, databook):
        """Returns XLS representation of DataBook."""

        wb = xlwt.Workbook(encoding='utf8')

        for i, dset in enumerate(databook._datasets):
            ws = wb.add_sheet(dset.title if dset.title else 'Sheet%s' % (i))

            cls.dset_sheet(dset, ws)

        stream = BytesIO()
        wb.save(stream)
        return stream.getvalue()

    @classmethod
    def import_set(cls, dset, in_stream, headers=True):
        """Returns databook from XLS stream."""

        dset.wipe()

        xls_book = xlrd.open_workbook(file_contents=in_stream.read())
        sheet = xls_book.sheet_by_index(0)

        dset.title = sheet.name

        for i in range(sheet.nrows):
            if i == 0 and headers:
                dset.headers = sheet.row_values(0)
            else:
                dset.append([
                    val if typ != xlrd.XL_CELL_ERROR else xlrd.error_text_from_code[val]
                    for val, typ in zip(sheet.row_values(i), sheet.row_types(i))
                ])

    @classmethod
    def import_book(cls, dbook, in_stream, headers=True):
        """Returns databook from XLS stream."""

        dbook.wipe()

        xls_book = xlrd.open_workbook(file_contents=in_stream)

        for sheet in xls_book.sheets():
            data = tablib.Dataset()
            data.title = sheet.name

            for i in range(sheet.nrows):
                if i == 0 and headers:
                    data.headers = sheet.row_values(0)
                else:
                    data.append(sheet.row_values(i))

            dbook.add_sheet(data)

    @classmethod
    def dset_sheet(cls, dataset, ws):
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
