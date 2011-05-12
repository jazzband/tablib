# file openpyxl/workbook.py

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

"""Workbook is the top-level container for all document information."""

__docformat__ = "restructuredtext en"

# Python stdlib imports
import datetime
import os

# package imports
from .worksheet import Worksheet
from .writer.dump_worksheet import DumpWorksheet, save_dump
from .writer.strings import StringTableBuilder
from .namedrange import NamedRange
from .style import Style
from .writer.excel import save_workbook
from .shared.exc import ReadOnlyWorkbookException


class DocumentProperties(object):
    """High-level properties of the document."""

    def __init__(self):
        self.creator = 'Unknown'
        self.last_modified_by = self.creator
        self.created = datetime.datetime.now()
        self.modified = datetime.datetime.now()
        self.title = 'Untitled'
        self.subject = ''
        self.description = ''
        self.keywords = ''
        self.category = ''
        self.company = 'Microsoft Corporation'


class DocumentSecurity(object):
    """Security information about the document."""

    def __init__(self):
        self.lock_revision = False
        self.lock_structure = False
        self.lock_windows = False
        self.revision_password = ''
        self.workbook_password = ''


class Workbook(object):
    """Workbook is the container for all other parts of the document."""

    def __init__(self, optimized_write = False):
        self.worksheets = []
        self._active_sheet_index = 0
        self._named_ranges = []
        self.properties = DocumentProperties()
        self.style = Style()
        self.security = DocumentSecurity()
        self.__optimized_write = optimized_write
        self.__optimized_read = False
        self.strings_table_builder = StringTableBuilder()

        if not optimized_write:
            self.worksheets.append(Worksheet(self))

    def _set_optimized_read(self):
        self.__optimized_read = True

    def get_active_sheet(self):
        """Returns the current active sheet."""
        return self.worksheets[self._active_sheet_index]

    def create_sheet(self, index = None):
        """Create a worksheet (at an optional index).

        :param index: optional position at which the sheet will be inserted
        :type index: int

        """

        if self.__optimized_read:
            raise ReadOnlyWorkbookException('Cannot create new sheet in a read-only workbook')

        if self.__optimized_write :
            new_ws = DumpWorksheet(parent_workbook = self)
        else:
            new_ws = Worksheet(parent_workbook = self)

        self.add_sheet(worksheet = new_ws, index = index)
        return new_ws

    def add_sheet(self, worksheet, index = None):
        """Add an existing worksheet (at an optional index)."""
        if index is None:
            index = len(self.worksheets)
        self.worksheets.insert(index, worksheet)

    def remove_sheet(self, worksheet):
        """Remove a worksheet from this workbook."""
        self.worksheets.remove(worksheet)

    def get_sheet_by_name(self, name):
        """Returns a worksheet by its name.

        Returns None if no worksheet has the name specified.

        :param name: the name of the worksheet to look for
        :type name: string

        """
        requested_sheet = None
        for sheet in self.worksheets:
            if sheet.title == name:
                requested_sheet = sheet
                break
        return requested_sheet

    def get_index(self, worksheet):
        """Return the index of the worksheet."""
        return self.worksheets.index(worksheet)

    def get_sheet_names(self):
        """Returns the list of the names of worksheets in the workbook.

        Names are returned in the worksheets order.

        :rtype: list of strings

        """
        return [s.title for s in self.worksheets]

    def create_named_range(self, name, worksheet, range):
        """Create a new named_range on a worksheet"""
        assert isinstance(worksheet, Worksheet)
        named_range = NamedRange(name, [(worksheet, range)])
        self.add_named_range(named_range)

    def get_named_ranges(self):
        """Return all named ranges"""
        return self._named_ranges

    def add_named_range(self, named_range):
        """Add an existing named_range to the list of named_ranges."""
        self._named_ranges.append(named_range)

    def get_named_range(self, name):
        """Return the range specified by name."""
        requested_range = None
        for named_range in self._named_ranges:
            if named_range.name == name:
                requested_range = named_range
                break
        return requested_range

    def remove_named_range(self, named_range):
        """Remove a named_range from this workbook."""
        self._named_ranges.remove(named_range)

    def save(self, filename):
        """ shortcut """
        if self.__optimized_write:
            save_dump(self, filename)
        else:
            save_workbook(self, filename)
