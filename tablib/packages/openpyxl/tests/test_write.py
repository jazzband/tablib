# file openpyxl/tests/test_write.py

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
from StringIO import StringIO
import os.path

# 3rd party imports
from nose.tools import eq_, with_setup, raises

# package imports
from openpyxl.tests.helper import TMPDIR, DATADIR, \
        assert_equals_file_content, clean_tmpdir, make_tmpdir
from openpyxl.workbook import Workbook
from openpyxl.reader.excel import load_workbook
from openpyxl.writer.excel import save_workbook, save_virtual_workbook, \
        ExcelWriter
from openpyxl.writer.workbook import write_workbook, write_workbook_rels
from openpyxl.writer.worksheet import write_worksheet, write_worksheet_rels
from openpyxl.writer.strings import write_string_table
from openpyxl.writer.styles import StyleWriter


@with_setup(setup = make_tmpdir, teardown = clean_tmpdir)
def test_write_empty_workbook():
    wb = Workbook()
    dest_filename = os.path.join(TMPDIR, 'empty_book.xlsx')
    save_workbook(wb, dest_filename)
    assert os.path.isfile(dest_filename)


def test_write_virtual_workbook():
    old_wb = Workbook()
    saved_wb = save_virtual_workbook(old_wb)
    new_wb = load_workbook(StringIO(saved_wb))
    assert new_wb


def test_write_workbook_rels():
    wb = Workbook()
    content = write_workbook_rels(wb)
    assert_equals_file_content(os.path.join(DATADIR, 'writer', 'expected', \
            'workbook.xml.rels'), content)


def test_write_workbook():
    wb = Workbook()
    content = write_workbook(wb)
    assert_equals_file_content(os.path.join(DATADIR, 'writer', 'expected', \
            'workbook.xml'), content)


def test_write_string_table():
    table = {'hello': 1, 'world': 2, 'nice': 3}
    content = write_string_table(table)
    assert_equals_file_content(os.path.join(DATADIR, 'writer', 'expected', \
            'sharedStrings.xml'), content)


def test_write_worksheet():
    wb = Workbook()
    ws = wb.create_sheet()
    ws.cell('F42').value = 'hello'
    content = write_worksheet(ws, {'hello': 0}, {})
    assert_equals_file_content(os.path.join(DATADIR, 'writer', 'expected', \
            'sheet1.xml'), content)


def test_write_hidden_worksheet():
    wb = Workbook()
    ws = wb.create_sheet()
    ws.sheet_state = ws.SHEETSTATE_HIDDEN
    ws.cell('F42').value = 'hello'
    content = write_worksheet(ws, {'hello': 0}, {})
    assert_equals_file_content(os.path.join(DATADIR, 'writer', 'expected', \
            'sheet1.xml'), content)


def test_write_formula():
    wb = Workbook()
    ws = wb.create_sheet()
    ws.cell('F1').value = 10
    ws.cell('F2').value = 32
    ws.cell('F3').value = '=F1+F2'
    content = write_worksheet(ws, {}, {})
    assert_equals_file_content(os.path.join(DATADIR, 'writer', 'expected', \
            'sheet1_formula.xml'), content)


def test_write_style():
    wb = Workbook()
    ws = wb.create_sheet()
    ws.cell('F1').value = '13%'
    style_id_by_hash = StyleWriter(wb).get_style_by_hash()
    content = write_worksheet(ws, {}, style_id_by_hash)
    assert_equals_file_content(os.path.join(DATADIR, 'writer', 'expected', \
            'sheet1_style.xml'), content)


def test_write_height():
    wb = Workbook()
    ws = wb.create_sheet()
    ws.cell('F1').value = 10
    ws.row_dimensions[ws.cell('F1').row].height = 30
    content = write_worksheet(ws, {}, {})
    assert_equals_file_content(os.path.join(DATADIR, 'writer', 'expected', \
            'sheet1_height.xml'), content)


def test_write_hyperlink():
    wb = Workbook()
    ws = wb.create_sheet()
    ws.cell('A1').value = "test"
    ws.cell('A1').hyperlink = "http://test.com"
    content = write_worksheet(ws, {'test': 0}, {})
    assert_equals_file_content(os.path.join(DATADIR, 'writer', 'expected', \
        'sheet1_hyperlink.xml'), content)


def test_write_hyperlink_rels():
    wb = Workbook()
    ws = wb.create_sheet()
    eq_(0, len(ws.relationships))
    ws.cell('A1').value = "test"
    ws.cell('A1').hyperlink = "http://test.com/"
    eq_(1, len(ws.relationships))
    ws.cell('A2').value = "test"
    ws.cell('A2').hyperlink = "http://test2.com/"
    eq_(2, len(ws.relationships))
    content = write_worksheet_rels(ws, 1)
    assert_equals_file_content(os.path.join(DATADIR, 'writer', 'expected', \
            'sheet1_hyperlink.xml.rels'), content)


def test_hyperlink_value():
    wb = Workbook()
    ws = wb.create_sheet()
    ws.cell('A1').hyperlink = "http://test.com"
    eq_("http://test.com", ws.cell('A1').value)
    ws.cell('A1').value = "test"
    eq_("test", ws.cell('A1').value)

def test_write_auto_filter():
    wb = Workbook()
    ws = wb.create_sheet()
    ws.cell('F42').value = 'hello'
    ws.auto_filter = 'A1:F1'
    content = write_worksheet(ws, {'hello': 0}, {})
    assert_equals_file_content(os.path.join(DATADIR, 'writer', 'expected', \
            'sheet1_auto_filter.xml'), content)

def test_freeze_panes_horiz():
    wb = Workbook()
    ws = wb.create_sheet()
    ws.cell('F42').value = 'hello'
    ws.freeze_panes = 'A4'
    content = write_worksheet(ws, {'hello': 0}, {})
    assert_equals_file_content(os.path.join(DATADIR, 'writer', 'expected', \
            'sheet1_freeze_panes_horiz.xml'), content)

def test_freeze_panes_vert():
    wb = Workbook()
    ws = wb.create_sheet()
    ws.cell('F42').value = 'hello'
    ws.freeze_panes = 'D1'
    content = write_worksheet(ws, {'hello': 0}, {})
    assert_equals_file_content(os.path.join(DATADIR, 'writer', 'expected', \
            'sheet1_freeze_panes_vert.xml'), content)
    pass

def test_freeze_panes_both():
    wb = Workbook()
    ws = wb.create_sheet()
    ws.cell('F42').value = 'hello'
    ws.freeze_panes = 'D4'
    content = write_worksheet(ws, {'hello': 0}, {})
    assert_equals_file_content(os.path.join(DATADIR, 'writer', 'expected', \
            'sheet1_freeze_panes_both.xml'), content)


