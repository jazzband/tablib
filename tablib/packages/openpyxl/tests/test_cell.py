# file openpyxl/tests/test_cell.py

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

# Python stdlib imports
from datetime import time, datetime

# 3rd party imports
from nose.tools import eq_, raises, assert_raises

# package imports
from openpyxl.worksheet import Worksheet
from openpyxl.workbook import Workbook
from openpyxl.shared.exc import ColumnStringIndexException, \
        CellCoordinatesException, DataTypeException
from openpyxl.cell import column_index_from_string, \
        coordinate_from_string, get_column_letter, Cell, absolute_coordinate


def test_coordinates():
    column, row = coordinate_from_string('ZF46')
    eq_("ZF", column)
    eq_(46, row)


@raises(CellCoordinatesException)
def test_invalid_coordinate():
    coordinate_from_string('AAA')


def test_absolute():
    eq_('$ZF$51', absolute_coordinate('ZF51'))

def test_absolute_multiple():

    eq_('$ZF$51:$ZF$53', absolute_coordinate('ZF51:ZF$53'))


def test_column_index():
    eq_(10, column_index_from_string('J'))
    eq_(270, column_index_from_string('jJ'))
    eq_(7030, column_index_from_string('jjj'))


def test_bad_column_index():

    @raises(ColumnStringIndexException)
    def _check(bad_string):
        column_index_from_string(bad_string)

    bad_strings = ('JJJJ', '', '$', '1',)
    for bad_string in bad_strings:
        yield _check, bad_string


def test_column_letter_boundries():
    assert_raises(ColumnStringIndexException, get_column_letter, 0)
    assert_raises(ColumnStringIndexException, get_column_letter, 18279)


def test_column_letter():
    eq_('ZZZ', get_column_letter(18278))
    eq_('JJJ', get_column_letter(7030))
    eq_('AB', get_column_letter(28))
    eq_('AA', get_column_letter(27))
    eq_('Z', get_column_letter(26))


def test_initial_value():
    cell = Cell(None, 'A', 1, value = '17.5')
    eq_(cell.TYPE_NUMERIC, cell.data_type)


class TestCellValueTypes():

    @classmethod
    def setup_class(cls):
        cls.cell = Cell(None, 'A', 1)

    def test_1st(self):
        eq_(self.cell.TYPE_NULL, self.cell.data_type)

    def test_null(self):
        self.cell.value = None
        eq_(self.cell.TYPE_NULL, self.cell.data_type)

    def test_numeric(self):

        def check_numeric(value):
            self.cell.value = value
            eq_(self.cell.TYPE_NUMERIC, self.cell.data_type)

        values = (42, '4.2', '-42.000', '0', 0, 0.0001, '0.9999', '99E-02')
        for value in values:
            yield check_numeric, value

    def test_string(self):
        self.cell.value = 'hello'
        eq_(self.cell.TYPE_STRING, self.cell.data_type)

    def test_formula(self):
        self.cell.value = '=42'
        eq_(self.cell.TYPE_FORMULA, self.cell.data_type)

    def test_boolean(self):
        self.cell.value = True
        eq_(self.cell.TYPE_BOOL, self.cell.data_type)
        self.cell.value = False
        eq_(self.cell.TYPE_BOOL, self.cell.data_type)

    def test_error_codes(self):

        def check_error():
            eq_(self.cell.TYPE_ERROR, self.cell.data_type)

        for error_string in self.cell.ERROR_CODES.keys():
            self.cell.value = error_string
            yield check_error


def test_data_type_check():
    cell = Cell(None, 'A', 1)
    cell.bind_value(None)
    eq_(Cell.TYPE_NULL, cell._data_type)

    cell.bind_value('.0e000')
    eq_(Cell.TYPE_NUMERIC, cell._data_type)

    cell.bind_value('-0.e-0')
    eq_(Cell.TYPE_NUMERIC, cell._data_type)

    cell.bind_value('1E')
    eq_(Cell.TYPE_STRING, cell._data_type)

@raises(DataTypeException)
def test_set_bad_type():
    cell = Cell(None, 'A', 1)
    cell.set_value_explicit(1, 'q')


def test_time():

    def check_time(raw_value, coerced_value):
        cell.value = raw_value
        eq_(cell.value, coerced_value)
        eq_(cell.TYPE_NUMERIC, cell.data_type)

    wb = Workbook()
    ws = Worksheet(wb)
    cell = Cell(ws, 'A', 1)
    values = (('03:40:16', time(3, 40, 16)), ('03:40', time(3, 40)),)
    for raw_value, coerced_value in values:
        yield check_time, raw_value, coerced_value


def test_date_format_on_non_date():
    wb = Workbook()
    ws = Worksheet(wb)
    cell = Cell(ws, 'A', 1)
    cell.value = datetime.now()
    cell.value = 'testme'
    eq_('testme', cell.value)


def test_repr():
    wb = Workbook()
    ws = Worksheet(wb)
    cell = Cell(ws, 'A', 1)
    eq_(repr(cell), '<Cell Sheet1.A1>', 'Got bad repr: %s' % repr(cell))

def test_is_date():
    wb = Workbook()
    ws = Worksheet(wb)
    cell = Cell(ws, 'A', 1)
    cell.value = datetime.now()
    eq_(cell.is_date(), True)
    cell.value = 'testme'
    eq_('testme', cell.value)
    eq_(cell.is_date(), False)
