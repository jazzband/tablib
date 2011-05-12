# file openpyxl/tests/test_strings.py

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
from __future__ import with_statement
import os.path

# 3rd party imports
from nose.tools import eq_

# package imports
from openpyxl.tests.helper import DATADIR
from openpyxl.workbook import Workbook
from openpyxl.writer.strings import create_string_table
from openpyxl.reader.strings import read_string_table


def test_create_string_table():
    wb = Workbook()
    ws = wb.create_sheet()
    ws.cell('B12').value = 'hello'
    ws.cell('B13').value = 'world'
    ws.cell('D28').value = 'hello'
    table = create_string_table(wb)
    eq_({'hello': 1, 'world': 0}, table)


def test_read_string_table():
    with open(os.path.join(DATADIR, 'reader', 'sharedStrings.xml')) as handle:
        content = handle.read()
    string_table = read_string_table(content)
    eq_({0: 'This is cell A1 in Sheet 1', 1: 'This is cell G5'}, string_table)

def test_empty_string():
     with open(os.path.join(DATADIR, 'reader', 'sharedStrings-emptystring.xml')) as handle:
        content = handle.read()   
     string_table = read_string_table(content)
     eq_({0: 'Testing empty cell', 1:''}, string_table)

def test_formatted_string_table():
    with open(os.path.join(DATADIR, 'reader', 'shared-strings-rich.xml')) \
            as handle:
        content = handle.read()
    string_table = read_string_table(content)
    eq_({0: 'Welcome', 1: 'to the best shop in town',
            2: "     let's play "}, string_table)
