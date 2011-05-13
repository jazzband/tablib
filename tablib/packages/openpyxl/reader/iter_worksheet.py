# file openpyxl/reader/iter_worksheet.py

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

""" Iterators-based worksheet reader
*Still very raw*
"""

from ....compat import BytesIO as StringIO
import warnings
import operator
from functools import partial
from itertools import groupby, ifilter
from ..worksheet import Worksheet
from ..cell import coordinate_from_string, get_column_letter, Cell
from ..reader.excel import get_sheet_ids
from ..reader.strings import read_string_table
from ..reader.style import read_style_table, NumberFormat
from ..shared.date_time import SharedDate
from ..reader.worksheet import read_dimension
from ..shared.ooxml import (MIN_COLUMN, MAX_COLUMN, PACKAGE_WORKSHEETS,
    MAX_ROW, MIN_ROW, ARC_SHARED_STRINGS, ARC_APP, ARC_STYLE)
try:
    from xml.etree.cElementTree import iterparse
except ImportError:
    from xml.etree.ElementTree import iterparse


from zipfile import ZipFile
from .. import cell
import re
import tempfile
import zlib
import zipfile
import struct

TYPE_NULL = Cell.TYPE_NULL
MISSING_VALUE = None

RE_COORDINATE = re.compile('^([A-Z]+)([0-9]+)$')

SHARED_DATE = SharedDate()

_COL_CONVERSION_CACHE = dict((get_column_letter(i), i) for i in xrange(1, 18279))
def column_index_from_string(str_col, _col_conversion_cache=_COL_CONVERSION_CACHE):
    # we use a function argument to get indexed name lookup
    return _col_conversion_cache[str_col]
del _COL_CONVERSION_CACHE

RAW_ATTRIBUTES = ['row', 'column', 'coordinate', 'internal_value', 'data_type', 'style_id', 'number_format']

try:
    from collections import namedtuple
    BaseRawCell = namedtuple('RawCell', RAW_ATTRIBUTES)
except ImportError:

    # warnings.warn("""Unable to import 'namedtuple' module, this may cause  memory issues when using optimized reader. Please upgrade your Python installation to 2.6+""")

    class BaseRawCell(object):

        def __init__(self, *args):
            assert len(args)==len(RAW_ATTRIBUTES)

            for attr, val in zip(RAW_ATTRIBUTES, args):
                setattr(self, attr, val)

        def _replace(self, **kwargs):

            self.__dict__.update(kwargs)

            return self


class RawCell(BaseRawCell):
    """Optimized version of the :class:`openpyxl.cell.Cell`, using named tuples.

    Useful attributes are:

    * row
    * column
    * coordinate
    * internal_value

    You can also access if needed:

    * data_type
    * number_format

    """

    @property
    def is_date(self):
        res = (self.data_type == Cell.TYPE_NUMERIC
               and self.number_format is not None
               and ('d' in self.number_format
                    or 'm' in self.number_format
                    or 'y' in self.number_format
                    or 'h' in self.number_format
                    or 's' in self.number_format
                   ))

        return res

def iter_rows(workbook_name, sheet_name, xml_source, range_string = '', row_offset = 0, column_offset = 0):

    archive = get_archive_file(workbook_name)

    source = xml_source

    if range_string:
        min_col, min_row, max_col, max_row = get_range_boundaries(range_string, row_offset, column_offset)
    else:
        min_col, min_row, max_col, max_row = read_dimension(xml_source = source)
        min_col = column_index_from_string(min_col)
        max_col = column_index_from_string(max_col) + 1
        max_row += 6

    try:
        string_table = read_string_table(archive.read(ARC_SHARED_STRINGS))
    except KeyError:
        string_table = {}

    style_table = read_style_table(archive.read(ARC_STYLE))

    source.seek(0)
    p = iterparse(source)

    return get_squared_range(p, min_col, min_row, max_col, max_row, string_table, style_table)


def get_rows(p, min_column = MIN_COLUMN, min_row = MIN_ROW, max_column = MAX_COLUMN, max_row = MAX_ROW):

    return groupby(get_cells(p, min_row, min_column, max_row, max_column), operator.attrgetter('row'))

def get_cells(p, min_row, min_col, max_row, max_col, _re_coordinate=RE_COORDINATE):

    for _event, element in p:

        if element.tag == '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c':
            coord = element.get('r')
            column_str, row = _re_coordinate.match(coord).groups()

            row = int(row)
            column = column_index_from_string(column_str)

            if min_col <= column <= max_col and min_row <= row <= max_row:
                data_type = element.get('t', 'n')
                style_id = element.get('s')
                value = element.findtext('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                yield RawCell(row, column_str, coord, value, data_type, style_id, None)

        if element.tag == '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v':
            continue
        element.clear()



def get_range_boundaries(range_string, row = 0, column = 0):

    if ':' in range_string:
        min_range, max_range = range_string.split(':')
        min_col, min_row = coordinate_from_string(min_range)
        max_col, max_row = coordinate_from_string(max_range)

        min_col = column_index_from_string(min_col) + column
        max_col = column_index_from_string(max_col) + column
        min_row += row
        max_row += row

    else:
        min_col, min_row = coordinate_from_string(range_string)
        min_col = column_index_from_string(min_col)
        max_col = min_col + 1
        max_row = min_row

    return (min_col, min_row, max_col, max_row)

def get_archive_file(archive_name):

    return ZipFile(archive_name, 'r')

def get_xml_source(archive_file, sheet_name):

    return archive_file.read('%s/%s' % (PACKAGE_WORKSHEETS, sheet_name))

def get_missing_cells(row, columns):

    return dict([(column, RawCell(row, column, '%s%s' % (column, row), MISSING_VALUE, TYPE_NULL, None, None)) for column in columns])

def get_squared_range(p, min_col, min_row, max_col, max_row, string_table, style_table):

    expected_columns = [get_column_letter(ci) for ci in xrange(min_col, max_col)]

    current_row = min_row
    for row, cells in get_rows(p, min_row = min_row, max_row = max_row, min_column = min_col, max_column = max_col):
        full_row = []
        if current_row < row:

            for gap_row in xrange(current_row, row):

                dummy_cells = get_missing_cells(gap_row, expected_columns)

                yield tuple([dummy_cells[column] for column in expected_columns])

                current_row = row

        temp_cells = list(cells)

        retrieved_columns = dict([(c.column, c) for c in temp_cells])

        missing_columns = list(set(expected_columns) - set(retrieved_columns.keys()))

        replacement_columns = get_missing_cells(row, missing_columns)

        for column in expected_columns:

            if column in retrieved_columns:
                cell = retrieved_columns[column]

                if cell.style_id is not None:
                    style = style_table[int(cell.style_id)]
                    cell = cell._replace(number_format = style.number_format.format_code) #pylint: disable-msg=W0212
                if cell.internal_value is not None:
                    if cell.data_type == Cell.TYPE_STRING:
                        cell = cell._replace(internal_value = string_table[int(cell.internal_value)]) #pylint: disable-msg=W0212
                    elif cell.data_type == Cell.TYPE_BOOL:
                        cell = cell._replace(internal_value = cell.internal_value == 'True')
                    elif cell.is_date:
                        cell = cell._replace(internal_value = SHARED_DATE.from_julian(float(cell.internal_value)))
                    elif cell.data_type == Cell.TYPE_NUMERIC:
                        cell = cell._replace(internal_value = float(cell.internal_value))
                full_row.append(cell)

            else:
                full_row.append(replacement_columns[column])

        current_row = row + 1

        yield tuple(full_row)

#------------------------------------------------------------------------------

class IterableWorksheet(Worksheet):

    def __init__(self, parent_workbook, title, workbook_name,
            sheet_codename, xml_source):

        Worksheet.__init__(self, parent_workbook, title)
        self._workbook_name = workbook_name
        self._sheet_codename = sheet_codename
        self._xml_source = xml_source

    def iter_rows(self, range_string = '', row_offset = 0, column_offset = 0):
        """ Returns a squared range based on the `range_string` parameter,
        using generators.

        :param range_string: range of cells (e.g. 'A1:C4')
        :type range_string: string

        :param row: row index of the cell (e.g. 4)
        :type row: int

        :param column: column index of the cell (e.g. 3)
        :type column: int

        :rtype: generator

        """

        return iter_rows(workbook_name = self._workbook_name,
                         sheet_name = self._sheet_codename,
                         xml_source = self._xml_source,
                         range_string = range_string,
                         row_offset = row_offset,
                         column_offset = column_offset)

    def cell(self, *args, **kwargs):

        raise NotImplementedError("use 'iter_rows()' instead")

    def range(self, *args, **kwargs):

        raise NotImplementedError("use 'iter_rows()' instead")

def unpack_worksheet(archive, filename):

    temp_file = tempfile.TemporaryFile(mode='r+', prefix='openpyxl.', suffix='.unpack.temp')

    zinfo = archive.getinfo(filename)

    if zinfo.compress_type == zipfile.ZIP_STORED:
        decoder = None
    elif zinfo.compress_type == zipfile.ZIP_DEFLATED:
        decoder = zlib.decompressobj(-zlib.MAX_WBITS)
    else:
        raise zipfile.BadZipFile("Unrecognized compression method")

    archive.fp.seek(_get_file_offset(archive, zinfo))
    bytes_to_read = zinfo.compress_size

    while True:
        buff = archive.fp.read(min(bytes_to_read, 102400))
        if not buff:
            break
        bytes_to_read -= len(buff)
        if decoder:
            buff = decoder.decompress(buff)
        temp_file.write(buff)

    if decoder:
        temp_file.write(decoder.decompress('Z'))

    return temp_file

def _get_file_offset(archive, zinfo):

    try:
        return zinfo.file_offset
    except AttributeError:
        # From http://stackoverflow.com/questions/3781261/how-to-simulate-zipfile-open-in-python-2-5

        # Seek over the fixed size fields to the "file name length" field in
        # the file header (26 bytes). Unpack this and the "extra field length"
        # field ourselves as info.extra doesn't seem to be the correct length.
        archive.fp.seek(zinfo.header_offset + 26)
        file_name_len, extra_len = struct.unpack("<HH", archive.fp.read(4))
        return zinfo.header_offset + 30 + file_name_len + extra_len
