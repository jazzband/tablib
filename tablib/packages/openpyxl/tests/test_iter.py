# file openpyxl/tests/test_iter.py

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

from nose.tools import eq_, raises, assert_raises
import os.path as osp
from openpyxl.tests.helper import DATADIR
from openpyxl.reader.iter_worksheet import get_range_boundaries
from openpyxl.reader.excel import load_workbook
import datetime

class TestWorksheet(object):

    workbook_name = osp.join(DATADIR, 'genuine', 'empty.xlsx')

class TestText(TestWorksheet):
    sheet_name = 'Sheet1 - Text'

    expected = [['This is cell A1 in Sheet 1', None, None, None, None, None, None],
                [None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None],
                [None, None, None, None, None, None, 'This is cell G5'], ]

    def test_read_fast_integrated(self):

        wb = load_workbook(filename = self.workbook_name, use_iterators = True)
        ws = wb.get_sheet_by_name(name = self.sheet_name)

        for row, expected_row in zip(ws.iter_rows(), self.expected):

            row_values = [x.internal_value for x in row]

            eq_(row_values, expected_row)


    def test_get_boundaries_range(self):

        eq_(get_range_boundaries('C1:C4'), (3, 1, 3, 4))

    def test_get_boundaries_one(self):


        eq_(get_range_boundaries('C1'), (3, 1, 4, 1))

    def test_read_single_cell_range(self):

        wb = load_workbook(filename = self.workbook_name, use_iterators = True)
        ws = wb.get_sheet_by_name(name = self.sheet_name)

        eq_('This is cell A1 in Sheet 1', list(ws.iter_rows('A1'))[0][0].internal_value)

class TestIntegers(TestWorksheet):

    sheet_name = 'Sheet2 - Numbers'

    expected = [[x + 1] for x in xrange(30)]

    query_range = 'D1:E30'

    def test_read_fast_integrated(self):

        wb = load_workbook(filename = self.workbook_name, use_iterators = True)
        ws = wb.get_sheet_by_name(name = self.sheet_name)

        for row, expected_row in zip(ws.iter_rows(self.query_range), self.expected):

            row_values = [x.internal_value for x in row]

            eq_(row_values, expected_row)

class TestFloats(TestWorksheet):

    sheet_name = 'Sheet2 - Numbers'
    query_range = 'K1:L30'
    expected = expected = [[(x + 1) / 100.0] for x in xrange(30)]

class TestDates(TestWorksheet):

    sheet_name = 'Sheet4 - Dates'

    def test_read_single_cell_date(self):

        wb = load_workbook(filename = self.workbook_name, use_iterators = True)
        ws = wb.get_sheet_by_name(name = self.sheet_name)

        eq_(datetime.datetime(1973, 5, 20), list(ws.iter_rows('A1'))[0][0].internal_value)
        eq_(datetime.datetime(1973, 5, 20, 9, 15, 2), list(ws.iter_rows('C1'))[0][0].internal_value)



