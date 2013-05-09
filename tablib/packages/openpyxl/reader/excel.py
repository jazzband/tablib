# file openpyxl/reader/excel.py

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

"""Read an xlsx file into Python"""

# Python stdlib imports
from zipfile import ZipFile, ZIP_DEFLATED, BadZipfile

# package imports
from openpyxl.shared.exc import OpenModeError, InvalidFileException
from openpyxl.shared.ooxml import (ARC_SHARED_STRINGS, ARC_CORE, ARC_WORKBOOK,
                                   PACKAGE_WORKSHEETS, ARC_STYLE, ARC_THEME)
from openpyxl.shared.compat import unicode, file
from openpyxl.workbook import Workbook, DocumentProperties
from openpyxl.reader.strings import read_string_table
from openpyxl.reader.style import read_style_table
from openpyxl.reader.workbook import (read_sheets_titles, read_named_ranges,
        read_properties_core, read_excel_base_date, get_sheet_ids)
from openpyxl.reader.worksheet import read_worksheet
from openpyxl.reader.iter_worksheet import unpack_worksheet
# Use exc_info for Python 2 compatibility with "except Exception[,/ as] e"
from sys import exc_info

try:
    # Python 2
    unicode
except NameError:
    # Python 3
    unicode = str

CENTRAL_DIRECTORY_SIGNATURE = '\x50\x4b\x05\x06'

def repair_central_directory(zipFile, is_file_instance):
    ''' trims trailing data from the central directory
    code taken from http://stackoverflow.com/a/7457686/570216, courtesy of Uri Cohen
    '''
    from StringIO import StringIO

    f = zipFile if is_file_instance else open(zipFile, 'r+b')
    data = f.read().decode("utf-8")
    pos = data.find(CENTRAL_DIRECTORY_SIGNATURE)  # End of central directory signature
    if (pos > 0):
        sio = StringIO(data)
        sio.seek(pos + 22)  # size of 'ZIP end of central directory record'
        sio.truncate()
        sio.seek(0)
        return sio

    f.seek(0)
    return f


def load_workbook(filename, use_iterators=False):
    """Open the given filename and return the workbook

    :param filename: the path to open or a file-like object
    :type filename: string or a file-like object open in binary mode c.f., :class:`zipfile.ZipFile`

    :param use_iterators: use lazy load for cells
    :type use_iterators: bool

    :rtype: :class:`openpyxl.workbook.Workbook`

    .. note::

        When using lazy load, all worksheets will be :class:`openpyxl.reader.iter_worksheet.IterableWorksheet`
        and the returned workbook will be read-only.

    """

    try:
        # Python 2
        is_file_instance = isinstance(filename, file)
    except NameError:
        # Python 3
        from io import BufferedReader
        is_file_instance = isinstance(filename, BufferedReader)


    if is_file_instance:
        # fileobject must have been opened with 'rb' flag
        # it is required by zipfile
        if 'b' not in filename.mode:
            raise OpenModeError("File-object must be opened in binary mode")

    try:
        archive = ZipFile(filename, 'r', ZIP_DEFLATED)
    except BadZipfile:
        try:
            f = repair_central_directory(filename, is_file_instance)
            archive = ZipFile(f, 'r', ZIP_DEFLATED)
        except BadZipfile:
            e = exc_info()[1]
            raise InvalidFileException(unicode(e))
    except (BadZipfile, RuntimeError, IOError, ValueError):
        e = exc_info()[1]
        raise InvalidFileException(unicode(e))
    wb = Workbook()

    if use_iterators:
        wb._set_optimized_read()

    try:
        _load_workbook(wb, archive, filename, use_iterators)
    except KeyError:
        e = exc_info()[1]
        raise InvalidFileException(unicode(e))

    archive.close()
    return wb

def _load_workbook(wb, archive, filename, use_iterators):

    valid_files = archive.namelist()

    # get workbook-level information
    try:
        wb.properties = read_properties_core(archive.read(ARC_CORE))
    except KeyError:
        wb.properties = DocumentProperties()

    try:
        string_table = read_string_table(archive.read(ARC_SHARED_STRINGS))
    except KeyError:
        string_table = {}
    try:
        wb.loaded_theme = archive.read(ARC_THEME)  # some writers don't output a theme, live with it (fixes #160)
    except KeyError:
        assert wb.loaded_theme == None, "even though the theme information is missing there is a theme object ?"

    style_table = read_style_table(archive.read(ARC_STYLE))

    wb.properties.excel_base_date = read_excel_base_date(xml_source=archive.read(ARC_WORKBOOK))

    # get worksheets
    wb.worksheets = []  # remove preset worksheet
    sheet_names = read_sheets_titles(archive.read(ARC_WORKBOOK))
    for i, sheet_name in enumerate(sheet_names):

        sheet_codename = 'sheet%d.xml' % (i + 1)
        worksheet_path = '%s/%s' % (PACKAGE_WORKSHEETS, sheet_codename)

        if not worksheet_path in valid_files:
            continue

        if not use_iterators:
            new_ws = read_worksheet(archive.read(worksheet_path), wb, sheet_name, string_table, style_table)
        else:
            xml_source = unpack_worksheet(archive, worksheet_path)
            new_ws = read_worksheet(xml_source, wb, sheet_name, string_table, style_table, filename, sheet_codename)
        wb.add_sheet(new_ws, index=i)

    wb._named_ranges = read_named_ranges(archive.read(ARC_WORKBOOK), wb)
