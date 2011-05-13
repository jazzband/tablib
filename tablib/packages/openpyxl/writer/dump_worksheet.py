# file openpyxl/writer/straight_worksheet.py

# Copyright (c) 2010 openpyxl
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# @license: http://www.opensource.org/licenses/mit-license.php
# @author: Eric Gazoni

"""Write worksheets to xml representations in an optimized way"""

import datetime
import os

from ..cell import column_index_from_string, get_column_letter, Cell
from ..worksheet import Worksheet
from ..shared.xmltools import XMLGenerator, get_document_content, \
        start_tag, end_tag, tag
from ..shared.date_time import SharedDate
from ..shared.ooxml import MAX_COLUMN, MAX_ROW
from tempfile import NamedTemporaryFile
from ..writer.excel import ExcelWriter
from ..writer.strings import write_string_table
from ..writer.styles import StyleWriter
from ..style import Style, NumberFormat

from ..shared.ooxml import ARC_SHARED_STRINGS, ARC_CONTENT_TYPES, \
        ARC_ROOT_RELS, ARC_WORKBOOK_RELS, ARC_APP, ARC_CORE, ARC_THEME, \
        ARC_STYLE, ARC_WORKBOOK, \
        PACKAGE_WORKSHEETS, PACKAGE_DRAWINGS, PACKAGE_CHARTS

STYLES = {'datetime' : {'type':Cell.TYPE_NUMERIC,
                        'style':'1'},
          'string':{'type':Cell.TYPE_STRING,
                    'style':'0'},
          'numeric':{'type':Cell.TYPE_NUMERIC,
                     'style':'0'},
          'formula':{'type':Cell.TYPE_FORMULA,
                    'style':'0'},
          'boolean':{'type':Cell.TYPE_BOOL,
                    'style':'0'},
        }

DATETIME_STYLE = Style()
DATETIME_STYLE.number_format.format_code = NumberFormat.FORMAT_DATE_YYYYMMDD2
BOUNDING_BOX_PLACEHOLDER = 'A1:%s%d' % (get_column_letter(MAX_COLUMN), MAX_ROW)

class DumpWorksheet(Worksheet):

    """
    .. warning::

        You shouldn't initialize this yourself, use :class:`openpyxl.workbook.Workbook` constructor instead,
        with `optimized_write = True`.
    """

    def __init__(self, parent_workbook):

        Worksheet.__init__(self, parent_workbook)

        self._max_col = 0
        self._max_row = 0
        self._parent = parent_workbook
        self._fileobj_header = NamedTemporaryFile(mode='r+', prefix='openpyxl.', suffix='.header', delete=False)
        self._fileobj_content = NamedTemporaryFile(mode='r+', prefix='openpyxl.', suffix='.content', delete=False)
        self._fileobj = NamedTemporaryFile(mode='w', prefix='openpyxl.', delete=False)
        self.doc = XMLGenerator(self._fileobj_content, 'utf-8')
        self.header = XMLGenerator(self._fileobj_header, 'utf-8')
        self.title = 'Sheet'

        self._shared_date = SharedDate()
        self._string_builder = self._parent.strings_table_builder

    @property
    def filename(self):
        return self._fileobj.name

    def write_header(self):

        doc = self.header

        start_tag(doc, 'worksheet',
                {'xml:space': 'preserve',
                'xmlns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
                'xmlns:r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'})
        start_tag(doc, 'sheetPr')
        tag(doc, 'outlinePr',
                {'summaryBelow': '1',
                'summaryRight': '1'})
        end_tag(doc, 'sheetPr')
        tag(doc, 'dimension', {'ref': 'A1:%s' % (self.get_dimensions())})
        start_tag(doc, 'sheetViews')
        start_tag(doc, 'sheetView', {'workbookViewId': '0'})
        tag(doc, 'selection', {'activeCell': 'A1',
                'sqref': 'A1'})
        end_tag(doc, 'sheetView')
        end_tag(doc, 'sheetViews')
        tag(doc, 'sheetFormatPr', {'defaultRowHeight': '15'})
        start_tag(doc, 'sheetData')

    def close(self):

        self._close_content()
        self._close_header()

        self._write_fileobj(self._fileobj_header)
        self._write_fileobj(self._fileobj_content)

        self._fileobj.close()

    def _write_fileobj(self, fobj):

        fobj.flush()
        fobj.seek(0)

        while True:
            chunk = fobj.read(4096)
            if not chunk:
                break
            self._fileobj.write(chunk)

        fobj.close()
        os.remove(fobj.name)

        self._fileobj.flush()

    def _close_header(self):

        doc = self.header
        #doc.endDocument()

    def _close_content(self):

        doc = self.doc
        end_tag(doc, 'sheetData')

        end_tag(doc, 'worksheet')
        #doc.endDocument()

    def get_dimensions(self):

        if not self._max_col or not self._max_row:
            return 'A1'
        else:
            return '%s%d' % (get_column_letter(self._max_col), (self._max_row))

    def append(self, row):

        """
        :param row: iterable containing values to append
        :type row: iterable
        """

        doc = self.doc

        self._max_row += 1
        span = len(row)
        self._max_col = max(self._max_col, span)

        row_idx = self._max_row

        attrs = {'r': '%d' % row_idx,
                 'spans': '1:%d' % span}

        start_tag(doc, 'row', attrs)

        for col_idx, cell in enumerate(row):

            if cell is None:
                continue

            coordinate = '%s%d' % (get_column_letter(col_idx+1), row_idx)
            attributes = {'r': coordinate}

            if isinstance(cell, bool):
                dtype = 'boolean'
            elif isinstance(cell, (int, float)):
                dtype = 'numeric'
            elif isinstance(cell, (datetime.datetime, datetime.date)):
                dtype = 'datetime'
                cell = self._shared_date.datetime_to_julian(cell)
                attributes['s'] = STYLES[dtype]['style']
            elif cell and cell[0] == '=':
                dtype = 'formula'
            else:
                dtype = 'string'
                cell = self._string_builder.add(cell)

            attributes['t'] = STYLES[dtype]['type']

            start_tag(doc, 'c', attributes)

            if dtype == 'formula':
                tag(doc, 'f', body = '%s' % cell[1:])
                tag(doc, 'v')
            else:
                tag(doc, 'v', body = '%s' % cell)

            end_tag(doc, 'c')


        end_tag(doc, 'row')


def save_dump(workbook, filename):

    writer = ExcelDumpWriter(workbook)
    writer.save(filename)
    return True

class ExcelDumpWriter(ExcelWriter):

    def __init__(self, workbook):

        self.workbook = workbook
        self.style_writer = StyleDumpWriter(workbook)
        self.style_writer._style_list.append(DATETIME_STYLE)

    def _write_string_table(self, archive):

        shared_string_table = self.workbook.strings_table_builder.get_table()
        archive.writestr(ARC_SHARED_STRINGS,
                write_string_table(shared_string_table))

        return shared_string_table

    def _write_worksheets(self, archive, shared_string_table, style_writer):

        for i, sheet in enumerate(self.workbook.worksheets):
            sheet.write_header()
            sheet.close()
            archive.write(sheet.filename, PACKAGE_WORKSHEETS + '/sheet%d.xml' % (i + 1))
            os.remove(sheet.filename)


class StyleDumpWriter(StyleWriter):

    def _get_style_list(self, workbook):
        return []

