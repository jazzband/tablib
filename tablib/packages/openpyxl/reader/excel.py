# file openpyxl/reader/excel.py

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

"""Read an xlsx file into Python"""

# Python stdlib imports
from zipfile import ZipFile, ZIP_DEFLATED, BadZipfile

# package imports
from ..shared.exc import OpenModeError, InvalidFileException
from ..shared.ooxml import ARC_SHARED_STRINGS, ARC_CORE, ARC_APP, \
        ARC_WORKBOOK, PACKAGE_WORKSHEETS, ARC_STYLE
from ..workbook import Workbook
from ..reader.strings import read_string_table
from ..reader.style import read_style_table
from ..reader.workbook import read_sheets_titles, read_named_ranges, \
        read_properties_core, get_sheet_ids
from ..reader.worksheet import read_worksheet
from ..reader.iter_worksheet import unpack_worksheet

def load_workbook(filename, use_iterators = False):
    """Open the given filename and return the workbook

    :param filename: the path to open
    :type filename: string

    :param use_iterators: use lazy load for cells
    :type use_iterators: bool

    :rtype: :class:`openpyxl.workbook.Workbook`

    .. note::

        When using lazy load, all worksheets will be :class:`openpyxl.reader.iter_worksheet.IterableWorksheet`
        and the returned workbook will be read-only.

    """

    if isinstance(filename, file):
        # fileobject must have been opened with 'rb' flag
        # it is required by zipfile
        if 'b' not in filename.mode:
            raise OpenModeError("File-object must be opened in binary mode")

    try:
        archive = ZipFile(filename, 'r', ZIP_DEFLATED)
    except (BadZipfile, RuntimeError, IOError, ValueError):
        raise InvalidFileException()
    wb = Workbook()

    if use_iterators:
        wb._set_optimized_read()

    try:
        _load_workbook(wb, archive, filename, use_iterators)
    except KeyError:
        raise InvalidFileException()
    finally:
        archive.close()
    return wb

def _load_workbook(wb, archive, filename, use_iterators):

    # get workbook-level information
    wb.properties = read_properties_core(archive.read(ARC_CORE))
    try:
        string_table = read_string_table(archive.read(ARC_SHARED_STRINGS))
    except KeyError:
        string_table = {}
    style_table = read_style_table(archive.read(ARC_STYLE))

    # get worksheets
    wb.worksheets = []  # remove preset worksheet
    sheet_names = read_sheets_titles(archive.read(ARC_APP))
    for i, sheet_name in enumerate(sheet_names):
        sheet_codename = 'sheet%d.xml' % (i + 1)
        worksheet_path = '%s/%s' % (PACKAGE_WORKSHEETS, sheet_codename)

        if not use_iterators:
            new_ws = read_worksheet(archive.read(worksheet_path), wb, sheet_name, string_table, style_table)
        else:
            xml_source = unpack_worksheet(archive, worksheet_path)
            new_ws = read_worksheet(xml_source, wb, sheet_name, string_table, style_table, filename, sheet_codename)
            #new_ws = read_worksheet(archive.read(worksheet_path), wb, sheet_name, string_table, style_table, filename, sheet_codename)
        wb.add_sheet(new_ws, index = i)

    wb._named_ranges = read_named_ranges(archive.read(ARC_WORKBOOK), wb)
