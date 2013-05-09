# file openpyxl/reader/worksheet.py

# Copyright (c) 2010-2011 openpyxl
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
# @author: see AUTHORS file

"""Reader for a single worksheet."""

# Python stdlib imports
try:
    from openpyxl.shared.compat import iterparse
except ImportError:
    from xml.etree.ElementTree import iterparse
try:
    # Python 2
    from StringIO import StringIO
except ImportError:
    # Python 3
    from io import BytesIO, StringIO

from openpyxl.cell import get_column_letter
from openpyxl.shared.xmltools import fromstring, QName

# package imports
from openpyxl.cell import Cell, coordinate_from_string
from openpyxl.worksheet import Worksheet, ColumnDimension

def _get_xml_iter(xml_source):

    if not hasattr(xml_source, 'name'):
        if isinstance(xml_source, str):
            return StringIO(xml_source)
        else:
            return StringIO(str(xml_source, 'utf-8'))
    else:
        xml_source.seek(0)
        return xml_source

def read_dimension(xml_source):

    source = _get_xml_iter(xml_source)

    it = iterparse(source)

    smax_col = None
    smax_row = None
    smin_col = None
    smin_row = None

    for event, element in it:

        if element.tag == '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}dimension':
            ref = element.get('ref')

            if ':' in ref:
                min_range, max_range = ref.split(':')
            else:
                min_range = max_range = ref

            min_col, min_row = coordinate_from_string(min_range)
            max_col, max_row = coordinate_from_string(max_range)

            return min_col, min_row, max_col, max_row

        if element.tag == '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c':
            # Supposedly the dimension is mandatory, but in practice it can be
            # left off sometimes, if so, observe the max/min extants and return
            # those instead.
            col, row = coordinate_from_string(element.get('r'))
            if smin_row is None:
                #initialize the observed max/min values
                smin_col = smax_col = col
                smin_row = smax_row = row
            else:
                #Keep track of the seen max and min (fallback if there's no dimension)
                smin_col = min(smin_col, col)
                smin_row = min(smin_row, row)
                smax_col = max(smax_col, col)
                smax_row = max(smax_row, row)
        else:
            element.clear()

    return smin_col, smin_row, smax_col, smax_row

def filter_cells(pair):
    (event, element) = pair

    return element.tag == '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'

def fast_parse(ws, xml_source, string_table, style_table):

    xmlns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    root = fromstring(xml_source)

    mergeCells = root.find(QName(xmlns, 'mergeCells').text)
    if mergeCells is not None:
        mergeCellNodes = mergeCells.findall(QName(xmlns, 'mergeCell').text)
        for mergeCell in mergeCellNodes:
            ws.merge_cells(mergeCell.get('ref'))

    source = _get_xml_iter(xml_source)

    it = iterparse(source)

    for event, element in filter(filter_cells, it):

        value = element.findtext('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')

        coordinate = element.get('r')
        style_id = element.get('s')
        if style_id is not None:
            ws._styles[coordinate] = style_table.get(int(style_id))

        if value is not None:
            data_type = element.get('t', 'n')
            if data_type == Cell.TYPE_STRING:
                value = string_table.get(int(value))

            ws.cell(coordinate).value = value

        # to avoid memory exhaustion, clear the item after use
        element.clear()

    cols = root.find(QName(xmlns, 'cols').text)
    if cols is not None:
        colNodes = cols.findall(QName(xmlns, 'col').text)
        for col in colNodes:
            min = int(col.get('min')) if col.get('min') else 1
            max = int(col.get('max')) if col.get('max') else 1
            for colId in range(min, max + 1):
                column = get_column_letter(colId)
                if column not in ws.column_dimensions:
                    ws.column_dimensions[column] = ColumnDimension(column)
                if col.get('width') is not None:
                    ws.column_dimensions[column].width = float(col.get('width'))
                if col.get('bestFit') == '1':
                    ws.column_dimensions[column].auto_size = True
                if col.get('hidden') == '1':
                    ws.column_dimensions[column].visible = False
                if col.get('outlineLevel') is not None:
                    ws.column_dimensions[column].outline_level = int(col.get('outlineLevel'))
                if col.get('collapsed') == '1':
                    ws.column_dimensions[column].collapsed = True
                if col.get('style') is not None:
                    ws.column_dimensions[column].style_index = col.get('style')

    printOptions = root.find(QName(xmlns, 'printOptions').text)
    if printOptions is not None:
        if printOptions.get('horizontalCentered') is not None:
            ws.page_setup.horizontalCentered = printOptions.get('horizontalCentered')
        if printOptions.get('verticalCentered') is not None:
            ws.page_setup.verticalCentered = printOptions.get('verticalCentered')

    pageMargins = root.find(QName(xmlns, 'pageMargins').text)
    if pageMargins is not None:
        if pageMargins.get('left') is not None:
            ws.page_margins.left = float(pageMargins.get('left'))
        if pageMargins.get('right') is not None:
            ws.page_margins.right = float(pageMargins.get('right'))
        if pageMargins.get('top') is not None:
            ws.page_margins.top = float(pageMargins.get('top'))
        if pageMargins.get('bottom') is not None:
            ws.page_margins.bottom = float(pageMargins.get('bottom'))
        if pageMargins.get('header') is not None:
            ws.page_margins.header = float(pageMargins.get('header'))
        if pageMargins.get('footer') is not None:
            ws.page_margins.footer = float(pageMargins.get('footer'))

    pageSetup = root.find(QName(xmlns, 'pageSetup').text)
    if pageSetup is not None:
        if pageSetup.get('orientation') is not None:
            ws.page_setup.orientation = pageSetup.get('orientation')
        if pageSetup.get('paperSize') is not None:
            ws.page_setup.paperSize = pageSetup.get('paperSize')
        if pageSetup.get('scale') is not None:
            ws.page_setup.top = pageSetup.get('scale')
        if pageSetup.get('fitToPage') is not None:
            ws.page_setup.fitToPage = pageSetup.get('fitToPage')
        if pageSetup.get('fitToHeight') is not None:
            ws.page_setup.fitToHeight = pageSetup.get('fitToHeight')
        if pageSetup.get('fitToWidth') is not None:
            ws.page_setup.fitToWidth = pageSetup.get('fitToWidth')
        if pageSetup.get('firstPageNumber') is not None:
            ws.page_setup.firstPageNumber = pageSetup.get('firstPageNumber')
        if pageSetup.get('useFirstPageNumber') is not None:
            ws.page_setup.useFirstPageNumber = pageSetup.get('useFirstPageNumber')

    headerFooter = root.find(QName(xmlns, 'headerFooter').text)
    if headerFooter is not None:
        oddHeader = headerFooter.find(QName(xmlns, 'oddHeader').text)
        if oddHeader is not None:
            ws.header_footer.setHeader(oddHeader.text)
        oddFooter = headerFooter.find(QName(xmlns, 'oddFooter').text)
        if oddFooter is not None:
            ws.header_footer.setFooter(oddFooter.text)

from openpyxl.reader.iter_worksheet import IterableWorksheet

def read_worksheet(xml_source, parent, preset_title, string_table,
                   style_table, workbook_name=None, sheet_codename=None):
    """Read an xml worksheet"""
    if workbook_name and sheet_codename:
        ws = IterableWorksheet(parent, preset_title, workbook_name,
                sheet_codename, xml_source, string_table)
    else:
        ws = Worksheet(parent, preset_title)
        fast_parse(ws, xml_source, string_table, style_table)
    return ws
