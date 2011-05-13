# file openpyxl/cell.py

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

"""Manage individual cells in a spreadsheet.

The Cell class is required to know its value and type, display options,
and any other features of an Excel cell.  Utilities for referencing
cells using Excel's 'A1' column/row nomenclature are also provided.

"""

__docformat__ = "restructuredtext en"

# Python stdlib imports
import datetime
import re

# package imports
from .shared.date_time import SharedDate
from .shared.exc import CellCoordinatesException, \
        ColumnStringIndexException, DataTypeException
from .style import NumberFormat

# constants
COORD_RE = re.compile('^[$]?([A-Z]+)[$]?(\d+)$')

ABSOLUTE_RE = re.compile('^[$]?([A-Z]+)[$]?(\d+)(:[$]?([A-Z]+)[$]?(\d+))?$')

def coordinate_from_string(coord_string):
    """Convert a coordinate string like 'B12' to a tuple ('B', 12)"""
    match = COORD_RE.match(coord_string.upper())
    if not match:
        msg = 'Invalid cell coordinates (%s)' % coord_string
        raise CellCoordinatesException(msg)
    column, row = match.groups()
    return (column, int(row))


def absolute_coordinate(coord_string):
    """Convert a coordinate to an absolute coordinate string (B12 -> $B$12)"""
    parts = ABSOLUTE_RE.match(coord_string).groups()

    if all(parts[-2:]):
        return '$%s$%s:$%s$%s' % (parts[0], parts[1], parts[3], parts[4])
    else:
        return '$%s$%s' % (parts[0], parts[1])


def column_index_from_string(column, fast = False):
    """Convert a column letter into a column number (e.g. B -> 2)

    Excel only supports 1-3 letter column names from A -> ZZZ, so we
    restrict our column names to 1-3 characters, each in the range A-Z.

    .. note::

        Fast mode is faster but does not check that all letters are capitals between A and Z

    """
    column = column.upper()

    clen = len(column)

    if not fast and not all('A' <= char <= 'Z' for char in column):
        msg = 'Column string must contain only characters A-Z: got %s' % column
        raise ColumnStringIndexException(msg)

    if clen == 1:
        return ord(column[0]) - 64
    elif clen == 2:
        return ((1 + (ord(column[0]) - 65)) * 26) + (ord(column[1]) - 64)
    elif clen == 3:
        return ((1 + (ord(column[0]) - 65)) * 676) + ((1 + (ord(column[1]) - 65)) * 26) + (ord(column[2]) - 64)
    elif clen > 3:
        raise ColumnStringIndexException('Column string index can not be longer than 3 characters')
    else:
        raise ColumnStringIndexException('Column string index can not be empty')


def get_column_letter(col_idx):
    """Convert a column number into a column letter (3 -> 'C')

    Right shift the column col_idx by 26 to find column letters in reverse
    order.  These numbers are 1-based, and can be converted to ASCII
    ordinals by adding 64.

    """
    # these indicies corrospond to A -> ZZZ and include all allowed
    # columns
    if not 1 <= col_idx <= 18278:
        msg = 'Column index out of bounds: %s' % col_idx
        raise ColumnStringIndexException(msg)
    ordinals = []
    temp = col_idx
    while temp:
        quotient, remainder = divmod(temp, 26)
        # check for exact division and borrow if needed
        if remainder == 0:
            quotient -= 1
            remainder = 26
        ordinals.append(remainder + 64)
        temp = quotient
    ordinals.reverse()
    return ''.join([chr(ordinal) for ordinal in ordinals])


class Cell(object):
    """Describes cell associated properties.

    Properties of interest include style, type, value, and address.

    """
    __slots__ = ('column',
                 'row',
                 '_value',
                 '_data_type',
                 'parent',
                 'xf_index',
                 '_hyperlink_rel')

    ERROR_CODES = {'#NULL!': 0,
                   '#DIV/0!': 1,
                   '#VALUE!': 2,
                   '#REF!': 3,
                   '#NAME?': 4,
                   '#NUM!': 5,
                   '#N/A': 6}

    TYPE_STRING = 's'
    TYPE_FORMULA = 'f'
    TYPE_NUMERIC = 'n'
    TYPE_BOOL = 'b'
    TYPE_NULL = 's'
    TYPE_INLINE = 'inlineStr'
    TYPE_ERROR = 'e'

    VALID_TYPES = [TYPE_STRING, TYPE_FORMULA, TYPE_NUMERIC, TYPE_BOOL,
                   TYPE_NULL, TYPE_INLINE, TYPE_ERROR]

    RE_PATTERNS = {
        'percentage': re.compile('^\-?[0-9]*\.?[0-9]*\s?\%$'),
        'time': re.compile('^(\d|[0-1]\d|2[0-3]):[0-5]\d(:[0-5]\d)?$'),
        'numeric': re.compile('^\-?([0-9]+\\.?[0-9]*|[0-9]*\\.?[0-9]+)((E|e)\-?[0-9]+)?$'), }

    def __init__(self, worksheet, column, row, value = None):
        self.column = column.upper()
        self.row = row
        # _value is the stored value, while value is the displayed value
        self._value = None
        self._hyperlink_rel = None
        self._data_type = self.TYPE_NULL
        if value:
            self.value = value
        self.parent = worksheet
        self.xf_index = 0

    def __repr__(self):
        return "<Cell %s.%s>" % (self.parent.title, self.get_coordinate())

    def check_string(self, value):
        """Check string coding, length, and line break character"""
        # convert to unicode string
        value = unicode(value)
        # string must never be longer than 32,767 characters
        # truncate if necessary
        value = value[:32767]
        # we require that newline is represented as "\n" in core,
        # not as "\r\n" or "\r"
        value = value.replace('\r\n', '\n')
        return value

    def check_numeric(self, value):
        """Cast value to int or float if necessary"""
        if not isinstance(value, (int, float)):
            try:
                value = int(value)
            except ValueError:
                value = float(value)
        return value

    def set_value_explicit(self, value = None, data_type = TYPE_STRING):
        """Coerce values according to their explicit type"""
        type_coercion_map = {
            self.TYPE_INLINE: self.check_string,
            self.TYPE_STRING: self.check_string,
            self.TYPE_FORMULA: unicode,
            self.TYPE_NUMERIC: self.check_numeric,
            self.TYPE_BOOL: bool, }
        try:
            self._value = type_coercion_map[data_type](value)
        except KeyError:
            if data_type not in self.VALID_TYPES:
                msg = 'Invalid data type: %s' % data_type
                raise DataTypeException(msg)
        self._data_type = data_type

    def data_type_for_value(self, value):
        """Given a value, infer the correct data type"""
        if value is None:
            data_type = self.TYPE_NULL
        elif value is True or value is False:
            data_type = self.TYPE_BOOL
        elif isinstance(value, (int, float)):
            data_type = self.TYPE_NUMERIC
        elif not value:
            data_type = self.TYPE_STRING
        elif isinstance(value, (datetime.datetime, datetime.date)):
            data_type = self.TYPE_NUMERIC
        elif isinstance(value, basestring) and value[0] == '=':
            data_type = self.TYPE_FORMULA
        elif self.RE_PATTERNS['numeric'].match(value):
            data_type = self.TYPE_NUMERIC
        elif value.strip() in self.ERROR_CODES:
            data_type = self.TYPE_ERROR
        else:
            data_type = self.TYPE_STRING
        return data_type

    def bind_value(self, value):
        """Given a value, infer type and display options."""
        self._data_type = self.data_type_for_value(value)
        if value is None:
            self.set_value_explicit('', self.TYPE_NULL)
            return True
        elif self._data_type == self.TYPE_STRING:
            # percentage detection
            percentage_search = self.RE_PATTERNS['percentage'].match(value)
            if percentage_search and value.strip() != '%':
                value = float(value.replace('%', '')) / 100.0
                self.set_value_explicit(value, self.TYPE_NUMERIC)
                self._set_number_format(NumberFormat.FORMAT_PERCENTAGE)
                return True
            # time detection
            time_search = self.RE_PATTERNS['time'].match(value)
            if time_search:
                sep_count = value.count(':') #pylint: disable-msg=E1103
                if sep_count == 1:
                    hours, minutes = [int(bit) for bit in value.split(':')] #pylint: disable-msg=E1103
                    seconds = 0
                elif sep_count == 2:
                    hours, minutes, seconds = \
                            [int(bit) for bit in value.split(':')] #pylint: disable-msg=E1103
                days = (hours / 24.0) + (minutes / 1440.0) + \
                        (seconds / 86400.0)
                self.set_value_explicit(days, self.TYPE_NUMERIC)
                self._set_number_format(NumberFormat.FORMAT_DATE_TIME3)
                return True
        if self._data_type == self.TYPE_NUMERIC:
            # date detection
            # if the value is a date, but not a date time, make it a
            # datetime, and set the time part to 0
            if isinstance(value, datetime.date) and not \
                    isinstance(value, datetime.datetime):
                value = datetime.datetime.combine(value, datetime.time())
            if isinstance(value, datetime.datetime):
                value = SharedDate().datetime_to_julian(date = value)
                self.set_value_explicit(value, self.TYPE_NUMERIC)
                self._set_number_format(NumberFormat.FORMAT_DATE_YYYYMMDD2)
                return True
        self.set_value_explicit(value, self._data_type)

    def _get_value(self):
        """Return the value, formatted as a date if needed"""
        value = self._value
        if self.is_date():
            value = SharedDate().from_julian(value)
        return value

    def _set_value(self, value):
        """Set the value and infer type and display options."""
        self.bind_value(value)

    value = property(_get_value, _set_value,
            doc = 'Get or set the value held in the cell.\n\n'
            ':rtype: depends on the value (string, float, int or '
            ':class:`datetime.datetime`)')

    def _set_hyperlink(self, val):
        """Set value and display for hyperlinks in a cell"""
        if self._hyperlink_rel is None:
            self._hyperlink_rel = self.parent.create_relationship("hyperlink")
        self._hyperlink_rel.target = val
        self._hyperlink_rel.target_mode = "External"
        if self._value is None:
            self.value = val

    def _get_hyperlink(self):
        """Return the hyperlink target or an empty string"""
        return self._hyperlink_rel is not None and \
                self._hyperlink_rel.target or ''

    hyperlink = property(_get_hyperlink, _set_hyperlink,
            doc = 'Get or set the hyperlink held in the cell.  '
            'Automatically sets the `value` of the cell with link text, '
            'but you can modify it afterwards by setting the '
            '`value` property, and the hyperlink will remain.\n\n'
            ':rtype: string')

    @property
    def hyperlink_rel_id(self):
        """Return the id pointed to by the hyperlink, or None"""
        return self._hyperlink_rel is not None and \
                self._hyperlink_rel.id or None

    def _set_number_format(self, format_code):
        """Set a new formatting code for numeric values"""
        self.style.number_format.format_code = format_code

    @property
    def has_style(self):
        """Check if the parent worksheet has a style for this cell"""
        return self.get_coordinate() in self.parent._styles #pylint: disable-msg=W0212

    @property
    def style(self):
        """Returns the :class:`openpyxl.style.Style` object for this cell"""
        return self.parent.get_style(self.get_coordinate())

    @property
    def data_type(self):
        """Return the data type represented by this cell"""
        return self._data_type

    def get_coordinate(self):
        """Return the coordinate string for this cell (e.g. 'B12')

        :rtype: string
        """
        return '%s%s' % (self.column, self.row)

    @property
    def address(self):
        """Return the coordinate string for this cell (e.g. 'B12')

        :rtype: string
        """
        return self.get_coordinate()

    def offset(self, row = 0, column = 0):
        """Returns a cell location relative to this cell.

        :param row: number of rows to offset
        :type row: int

        :param column: number of columns to offset
        :type column: int

        :rtype: :class:`openpyxl.cell.Cell`
        """
        offset_column = get_column_letter(column_index_from_string(
                column = self.column) + column)
        offset_row = self.row + row
        return self.parent.cell('%s%s' % (offset_column, offset_row))

    def is_date(self):
        """Returns whether the value is *probably* a date or not

        :rtype: bool
        """
        return (self.has_style
                and self.style.number_format.is_date_format()
                and isinstance(self._value, (int, float)))
