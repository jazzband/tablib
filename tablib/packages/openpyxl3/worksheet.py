# file openpyxl/worksheet.py

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

"""Worksheet is the 2nd-level container in Excel."""

# Python stdlib imports
import re

# package imports
from . import cell
from .cell import coordinate_from_string, \
    column_index_from_string, get_column_letter
from .shared.exc import SheetTitleException, \
    InsufficientCoordinatesException, CellCoordinatesException, \
    NamedRangeException
from .shared.password_hasher import hash_password
from .style import Style, DEFAULTS as DEFAULTS_STYLE
from .drawing import Drawing

_DEFAULTS_STYLE_HASH = hash(DEFAULTS_STYLE)

def flatten(results):

    rows = []

    for row in results:

        cells = []

        for cell in row:

            cells.append(cell.value)

        rows.append(tuple(cells))

    return tuple(rows)


class Relationship(object):
    """Represents many kinds of relationships."""
    # TODO: Use this object for workbook relationships as well as
    # worksheet relationships
    TYPES = {
        'hyperlink': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',
        'drawing':'http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing',
        #'worksheet': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet',
        #'sharedStrings': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings',
        #'styles': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles',
        #'theme': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme',
    }

    def __init__(self, rel_type):
        if rel_type not in self.TYPES:
            raise ValueError("Invalid relationship type %s" % rel_type)
        self.type = self.TYPES[rel_type]
        self.target = ""
        self.target_mode = ""
        self.id = ""


class PageSetup(object):
    """Information about page layout for this sheet"""
    pass


class HeaderFooter(object):
    """Information about the header/footer for this sheet."""
    pass


class SheetView(object):
    """Information about the visible portions of this sheet."""
    pass


class RowDimension(object):
    """Information about the display properties of a row."""
    __slots__ = ('row_index',
                 'height',
                 'visible',
                 'outline_level',
                 'collapsed',
                 'style_index',)

    def __init__(self, index = 0):
        self.row_index = index
        self.height = -1
        self.visible = True
        self.outline_level = 0
        self.collapsed = False
        self.style_index = None


class ColumnDimension(object):
    """Information about the display properties of a column."""
    __slots__ = ('column_index',
                 'width',
                 'auto_size',
                 'visible',
                 'outline_level',
                 'collapsed',
                 'style_index',)

    def __init__(self, index = 'A'):
        self.column_index = index
        self.width = -1
        self.auto_size = False
        self.visible = True
        self.outline_level = 0
        self.collapsed = False
        self.style_index = 0


class PageMargins(object):
    """Information about page margins for view/print layouts."""

    def __init__(self):
        self.left = self.right = 0.7
        self.top = self.bottom = 0.75
        self.header = self.footer = 0.3


class SheetProtection(object):
    """Information about protection of various aspects of a sheet."""

    def __init__(self):
        self.sheet = False
        self.objects = False
        self.scenarios = False
        self.format_cells = False
        self.format_columns = False
        self.format_rows = False
        self.insert_columns = False
        self.insert_rows = False
        self.insert_hyperlinks = False
        self.delete_columns = False
        self.delete_rows = False
        self.select_locked_cells = False
        self.sort = False
        self.auto_filter = False
        self.pivot_tables = False
        self.select_unlocked_cells = False
        self._password = ''

    def set_password(self, value = '', already_hashed = False):
        """Set a password on this sheet."""
        if not already_hashed:
            value = hash_password(value)
        self._password = value

    def _set_raw_password(self, value):
        """Set a password directly, forcing a hash step."""
        self.set_password(value, already_hashed = False)

    def _get_raw_password(self):
        """Return the password value, regardless of hash."""
        return self._password

    password = property(_get_raw_password, _set_raw_password,
            'get/set the password (if already hashed, '
            'use set_password() instead)')


class Worksheet(object):
    """Represents a worksheet.

    Do not create worksheets yourself,
    use :func:`.workbook.Workbook.create_sheet` instead

    """
    BREAK_NONE = 0
    BREAK_ROW = 1
    BREAK_COLUMN = 2

    SHEETSTATE_VISIBLE = 'visible'
    SHEETSTATE_HIDDEN = 'hidden'
    SHEETSTATE_VERYHIDDEN = 'veryHidden'

    def __init__(self, parent_workbook, title = 'Sheet'):
        self._parent = parent_workbook
        self._title = ''
        if not title:
            self.title = 'Sheet%d' % (1 + len(self._parent.worksheets))
        else:
            self.title = title
        self.row_dimensions = {}
        self.column_dimensions = {}
        self._cells = {}
        self._styles = {}
        self._charts = []
        self.relationships = []
        self.selected_cell = 'A1'
        self.active_cell = 'A1'
        self.sheet_state = self.SHEETSTATE_VISIBLE
        self.page_setup = PageSetup()
        self.page_margins = PageMargins()
        self.header_footer = HeaderFooter()
        self.sheet_view = SheetView()
        self.protection = SheetProtection()
        self.show_gridlines = True
        self.print_gridlines = False
        self.show_summary_below = True
        self.show_summary_right = True
        self.default_row_dimension = RowDimension()
        self.default_column_dimension = ColumnDimension()
        self._auto_filter = None
        self._freeze_panes = None

    def __repr__(self):
        return '<Worksheet "%s">' % self.title

    def garbage_collect(self):
        """Delete cells that are not storing a value."""
        delete_list = [coordinate for coordinate, cell in \
            self._cells.items() if (cell.value in ('', None) and \
            hash(cell.style) == _DEFAULTS_STYLE_HASH)]
        for coordinate in delete_list:
            del self._cells[coordinate]

    def get_cell_collection(self):
        """Return an unordered list of the cells in this worksheet."""
        return list(self._cells.values())

    def _set_title(self, value):
        """Set a sheet title, ensuring it is valid."""
        bad_title_char_re = re.compile(r'[\\*?:/\[\]]')
        if bad_title_char_re.search(value):
            msg = 'Invalid character found in sheet title'
            raise SheetTitleException(msg)

        # check if sheet_name already exists
        # do this *before* length check
        if self._parent.get_sheet_by_name(value):
            # use name, but append with lowest possible integer
            i = 1
            while self._parent.get_sheet_by_name('%s%d' % (value, i)):
                i += 1
            value = '%s%d' % (value, i)
        if len(value) > 31:
            msg = 'Maximum 31 characters allowed in sheet title'
            raise SheetTitleException(msg)
        self._title = value

    def _get_title(self):
        """Return the title for this sheet."""
        return self._title

    title = property(_get_title, _set_title, doc =
                     'Get or set the title of the worksheet. '
                     'Limited to 31 characters, no special characters.')

    def _set_auto_filter(self, range):
        # Normalize range to a str or None
        if not range:
            range = None
        elif isinstance(range, str):
            range = range.upper()
        else: # Assume a range
            range = range[0][0].address + ':' + range[-1][-1].address
        self._auto_filter = range

    def _get_auto_filter(self):
        return self._auto_filter

    auto_filter = property(_get_auto_filter, _set_auto_filter, doc =
                           'get or set auto filtering on columns')
    def _set_freeze_panes(self, topLeftCell):
        if not topLeftCell:
            topLeftCell = None
        elif isinstance(topLeftCell, str):
            topLeftCell = topLeftCell.upper()
        else: # Assume a cell
            topLeftCell = topLeftCell.address
        if topLeftCell == 'A1':
            topLeftCell = None
        self._freeze_panes = topLeftCell

    def _get_freeze_panes(self):
        return self._freeze_panes

    freeze_panes = property(_get_freeze_panes,_set_freeze_panes, doc =
                           "Get or set frozen panes")

    def cell(self, coordinate = None, row = None, column = None):
        """Returns a cell object based on the given coordinates.

        Usage: cell(coodinate='A15') **or** cell(row=15, column=1)

        If `coordinates` are not given, then row *and* column must be given.

        Cells are kept in a dictionary which is empty at the worksheet
        creation.  Calling `cell` creates the cell in memory when they
        are first accessed, to reduce memory usage.

        :param coordinate: coordinates of the cell (e.g. 'B12')
        :type coordinate: string

        :param row: row index of the cell (e.g. 4)
        :type row: int

        :param column: column index of the cell (e.g. 3)
        :type column: int

        :raise: InsufficientCoordinatesException when coordinate or (row and column) are not given

        :rtype: :class:`.cell.Cell`

        """
        if not coordinate:
            if  (row is None or column is None):
                msg = "You have to provide a value either for " \
                        "'coordinate' or for 'row' *and* 'column'"
                raise InsufficientCoordinatesException(msg)
            else:
                coordinate = '%s%s' % (get_column_letter(column + 1), row + 1)
        else:
            coordinate = coordinate.replace('$', '')

        return self._get_cell(coordinate)

    def _get_cell(self, coordinate):

        if not coordinate in self._cells:
            column, row = coordinate_from_string(coordinate)
            new_cell = cell.Cell(self, column, row)
            self._cells[coordinate] = new_cell
            if column not in self.column_dimensions:
                self.column_dimensions[column] = ColumnDimension(column)
            if row not in self.row_dimensions:
                self.row_dimensions[row] = RowDimension(row)
        return self._cells[coordinate]

    def get_highest_row(self):
        """Returns the maximum row index containing data
        
        :rtype: int
        """
        if self.row_dimensions:
            return max(self.row_dimensions.keys())
        else:
            return 1

    def get_highest_column(self):
        """Get the largest value for column currently stored.
        
        :rtype: int
        """
        if self.column_dimensions:
            return max([column_index_from_string(column_index)
                            for column_index in self.column_dimensions])
        else:
            return 1

    def calculate_dimension(self):
        """Return the minimum bounding range for all cells containing data."""
        return 'A1:%s%d' % (get_column_letter(self.get_highest_column()),
                            self.get_highest_row())

    def range(self, range_string, row = 0, column = 0):
        """Returns a 2D array of cells, with optional row and column offsets.

        :param range_string: cell range string or `named range` name
        :type range_string: string

        :param row: number of rows to offset
        :type row: int

        :param column: number of columns to offset
        :type column: int

        :rtype: tuples of tuples of :class:`.cell.Cell`

        """
        if ':' in range_string:
            # R1C1 range
            result = []
            min_range, max_range = range_string.split(':')
            min_col, min_row = coordinate_from_string(min_range)
            max_col, max_row = coordinate_from_string(max_range)
            if column:
                min_col = get_column_letter(
                        column_index_from_string(min_col) + column)
                max_col = get_column_letter(
                        column_index_from_string(max_col) + column)
            min_col = column_index_from_string(min_col)
            max_col = column_index_from_string(max_col)
            cache_cols = {}
            for col in range(min_col, max_col + 1):
                cache_cols[col] = get_column_letter(col)
            rows = range(min_row + row, max_row + row + 1)
            cols = range(min_col, max_col + 1)
            for row in rows:
                new_row = []
                for col in cols:
                    new_row.append(self.cell('%s%s' % (cache_cols[col], row)))
                result.append(tuple(new_row))
            return tuple(result)
        else:
            try:
                return self.cell(coordinate = range_string, row = row,
                        column = column)
            except CellCoordinatesException:
                pass

            # named range
            named_range = self._parent.get_named_range(range_string)
            if named_range is None:
                msg = '%s is not a valid range name' % range_string
                raise NamedRangeException(msg)

            result = []
            for destination in named_range.destinations:

                worksheet, cells_range = destination

                if worksheet is not self:
                    msg = 'Range %s is not defined on worksheet %s' % \
                            (cells_range, self.title)
                    raise NamedRangeException(msg)

                content = self.range(cells_range)

                if isinstance(content, tuple):
                    for cells in content:
                        result.extend(cells)
                else:
                    result.append(content)

            if len(result) == 1:
                return result[0]
            else:
                return tuple(result)

    def get_style(self, coordinate):
        """Return the style object for the specified cell."""
        if not coordinate in self._styles:
            self._styles[coordinate] = Style()
        return self._styles[coordinate]

    def create_relationship(self, rel_type):
        """Add a relationship for this sheet."""
        rel = Relationship(rel_type)
        self.relationships.append(rel)
        rel_id = self.relationships.index(rel)
        rel.id = 'rId' + str(rel_id + 1)
        return self.relationships[rel_id]

    def add_chart(self, chart):
        """ Add a chart to the sheet """

        chart._sheet = self
        self._charts.append(chart)

    def append(self, list_or_dict):
        """Appends a group of values at the bottom of the current sheet.
        
        * If it's a list: all values are added in order, starting from the first column
        * If it's a dict: values are assigned to the columns indicated by the keys (numbers or letters)
        
        :param list_or_dict: list or dict containing values to append
        :type list_or_dict: list/tuple or dict
        
        Usage:
        
        * append(['This is A1', 'This is B1', 'This is C1'])
        * **or** append({'A' : 'This is A1', 'C' : 'This is C1'})
        * **or** append({0 : 'This is A1', 2 : 'This is C1'})
        
        :raise: TypeError when list_or_dict is neither a list/tuple nor a dict
        
        """

        row_idx = len(self.row_dimensions)

        if isinstance(list_or_dict, (list, tuple)):

            for col_idx, content in enumerate(list_or_dict):

                self.cell(row = row_idx, column = col_idx).value = content

        elif isinstance(list_or_dict, dict):

            for col_idx, content in list_or_dict.items():

                if isinstance(col_idx, str):
                    col_idx = column_index_from_string(col_idx) - 1

                self.cell(row = row_idx, column = col_idx).value = content

        else:
            raise TypeError('list_or_dict must be a list or a dict')

    @property
    def rows(self):

        return self.range(self.calculate_dimension())

    @property
    def columns(self):

        max_row = self.get_highest_row()

        cols = []

        for col_idx in range(self.get_highest_column()):
            col = get_column_letter(col_idx+1)
            res = self.range('%s1:%s%d' % (col, col, max_row))
            cols.append(tuple([x[0] for x in res]))


        return tuple(cols)

