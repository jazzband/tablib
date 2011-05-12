
# file openpyxl/tests/test_dump.py

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

from openpyxl.workbook import Workbook
from openpyxl.cell import get_column_letter

from openpyxl.reader.excel import load_workbook

from openpyxl.writer.strings import StringTableBuilder

from tempfile import NamedTemporaryFile
import os
import shutil

def test_dump_sheet():

    test_file = NamedTemporaryFile(prefix='openpyxl.', suffix='.xlsx', delete=False) 
    test_file.close()
    test_filename = test_file.name

    wb = Workbook(optimized_write = True)

    ws = wb.create_sheet()

    letters = [get_column_letter(x+1) for x in xrange(20)]

    expected_rows = []

    for row in xrange(20):

        expected_rows.append(['%s%d' % (letter, row+1) for letter in letters])

    for row in xrange(20):

        expected_rows.append([(row+1) for letter in letters])

    for row in xrange(10):

        expected_rows.append([datetime(2010, ((x % 12)+1), row+1) for x in range(len(letters))])

    for row in xrange(20):

        expected_rows.append(['=%s%d' % (letter, row+1) for letter in letters])

    for row in expected_rows:

        ws.append(row)

    wb.save(test_filename)

    wb2 = load_workbook(test_filename, True)

    ws = wb2.worksheets[0]


    for ex_row, ws_row in zip(expected_rows[:-20], ws.iter_rows()):

        for ex_cell, ws_cell in zip(ex_row, ws_row):

            eq_(ex_cell, ws_cell.internal_value)

    os.remove(test_filename)


def test_table_builder():

    sb = StringTableBuilder()

    result = {'a':0, 'b':1, 'c':2, 'd':3}

    for letter in sorted(result.keys()):

        for x in range(5):

            sb.add(letter)

    table = dict(sb.get_table())

    for key,idx in result.iteritems():
        eq_(idx, table[key])
