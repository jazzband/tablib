# file openpyxl/tests/test_workbook.py

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

# 3rd party imports
from nose.tools import eq_, with_setup, raises
import os.path as osp

# package imports
from openpyxl.workbook import Workbook
from openpyxl.reader.excel import load_workbook
from openpyxl.namedrange import NamedRange
from openpyxl.shared.exc import ReadOnlyWorkbookException
from openpyxl.tests.helper import TMPDIR, clean_tmpdir, make_tmpdir

import datetime

def test_get_active_sheet():
    wb = Workbook()
    active_sheet = wb.get_active_sheet()
    eq_(active_sheet, wb.worksheets[0])


def test_create_sheet():
    wb = Workbook()
    new_sheet = wb.create_sheet(0)
    eq_(new_sheet, wb.worksheets[0])


@raises(ReadOnlyWorkbookException)
def test_create_sheet_readonly():
    wb = Workbook()
    wb._set_optimized_read()
    wb.create_sheet()


def test_remove_sheet():
    wb = Workbook()
    new_sheet = wb.create_sheet(0)
    wb.remove_sheet(new_sheet)
    assert new_sheet not in wb.worksheets


def test_get_sheet_by_name():
    wb = Workbook()
    new_sheet = wb.create_sheet()
    title = 'my sheet'
    new_sheet.title = title
    found_sheet = wb.get_sheet_by_name(title)
    eq_(new_sheet, found_sheet)


def test_get_index():
    wb = Workbook()
    new_sheet = wb.create_sheet(0)
    sheet_index = wb.get_index(new_sheet)
    eq_(sheet_index, 0)


def test_get_sheet_names():
    wb = Workbook()
    names = ['Sheet', 'Sheet1', 'Sheet2', 'Sheet3', 'Sheet4', 'Sheet5']
    for count in range(5):
        wb.create_sheet(0)
    actual_names = wb.get_sheet_names()
    eq_(sorted(actual_names), sorted(names))


def test_get_named_ranges():
    wb = Workbook()
    eq_(wb.get_named_ranges(), wb._named_ranges)


def test_add_named_range():
    wb = Workbook()
    new_sheet = wb.create_sheet()
    named_range = NamedRange('test_nr', [(new_sheet, 'A1')])
    wb.add_named_range(named_range)
    named_ranges_list = wb.get_named_ranges()
    assert named_range in named_ranges_list


def test_get_named_range():
    wb = Workbook()
    new_sheet = wb.create_sheet()
    named_range = NamedRange('test_nr', [(new_sheet, 'A1')])
    wb.add_named_range(named_range)
    found_named_range = wb.get_named_range('test_nr')
    eq_(named_range, found_named_range)


def test_remove_named_range():
    wb = Workbook()
    new_sheet = wb.create_sheet()
    named_range = NamedRange('test_nr', [(new_sheet, 'A1')])
    wb.add_named_range(named_range)
    wb.remove_named_range(named_range)
    named_ranges_list = wb.get_named_ranges()
    assert named_range not in named_ranges_list

@with_setup(setup = make_tmpdir, teardown = clean_tmpdir)
def test_add_local_named_range():
    wb = Workbook()
    new_sheet = wb.create_sheet()
    named_range = NamedRange('test_nr', [(new_sheet, 'A1')])
    named_range.local_only = True
    wb.add_named_range(named_range)
    dest_filename = osp.join(TMPDIR, 'local_named_range_book.xlsx')
    wb.save(dest_filename)


@with_setup(setup = make_tmpdir, teardown = clean_tmpdir)
def test_write_regular_date():

    today = datetime.datetime(2010, 1, 18, 14, 15, 20, 1600)

    book = Workbook()
    sheet = book.get_active_sheet()
    sheet.cell("A1").value = today
    dest_filename = osp.join(TMPDIR, 'date_read_write_issue.xlsx')
    book.save(dest_filename)

    test_book = load_workbook(dest_filename)
    test_sheet = test_book.get_active_sheet()

    eq_(test_sheet.cell("A1").value, today)
        
