# file openpyxl/worksheet.py
from openpyxl.shared.units import points_to_pixels
from openpyxl.shared import DEFAULT_COLUMN_WIDTH, DEFAULT_ROW_HEIGHT

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

"""Worksheet is the 2nd-level container in Excel."""

# Python stdlib imports
import re

# package imports
import openpyxl.cell
from openpyxl.cell import coordinate_from_string, \
    column_index_from_string, get_column_letter
from openpyxl.shared.exc import SheetTitleException, \
    InsufficientCoordinatesException, CellCoordinatesException, \
    NamedRangeException
from openpyxl.shared.password_hasher import hash_password
from openpyxl.style import Style, DEFAULTS as DEFAULTS_STYLE
from openpyxl.drawing import Drawing
from openpyxl.namedrange import NamedRangeContainingValue
from openpyxl.shared.compat import OrderedDict, unicode, xrange, basestring
from openpyxl.shared.compat.itertools import iteritems

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
        'image':'http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing'
        # 'worksheet': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet',
        # 'sharedStrings': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings',
        # 'styles': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles',
        # 'theme': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme',
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
    valid_setup = ("orientation", "paperSize", "scale", "fitToPage", "fitToHeight", "fitToWidth", "firstPageNumber", "useFirstPageNumber")
    valid_options = ("horizontalCentered", "verticalCentered")

    def __init__(self):
        self.orientation = self.paperSize = self.scale = self.fitToPage = self.fitToHeight = self.fitToWidth = self.firstPageNumber = self.useFirstPageNumber = None
        self.horizontalCentered = self.verticalCentered = None

    @property
    def setup(self):
        setupGroup = OrderedDict()
        for setup_name in self.valid_setup:
            setup_value = getattr(self, setup_name)
            if setup_value is not None:
                if setup_name == 'orientation':
                    setupGroup[setup_name] = '%s' % setup_value
                elif setup_name in ('paperSize', 'scale'):
                    setupGroup[setup_name] = '%d' % int(setup_value)
                elif setup_name in ('fitToHeight', 'fitToWidth') and int(setup_value) >= 0:
                    setupGroup[setup_name] = '%d' % int(setup_value)

        return setupGroup

    @property
    def options(self):
        optionsGroup = OrderedDict()
        for options_name in self.valid_options:
            options_value = getattr(self, options_name)
            if options_value is not None:
                if options_name in ('horizontalCentered', 'verticalCentered') and options_value:
                    optionsGroup[options_name] = '1'

        return optionsGroup


class HeaderFooterItem(object):
    """Individual left/center/right header/footer items

       Header & Footer ampersand codes:

       * &A   Inserts the worksheet name
       * &B   Toggles bold
       * &D or &[Date]   Inserts the current date
       * &E   Toggles double-underline
       * &F or &[File]   Inserts the workbook name
       * &I   Toggles italic
       * &N or &[Pages]   Inserts the total page count
       * &S   Toggles strikethrough
       * &T   Inserts the current time
       * &[Tab]   Inserts the worksheet name
       * &U   Toggles underline
       * &X   Toggles superscript
       * &Y   Toggles subscript
       * &P or &[Page]   Inserts the current page number
       * &P+n   Inserts the page number incremented by n
       * &P-n   Inserts the page number decremented by n
       * &[Path]   Inserts the workbook path
       * &&   Escapes the ampersand character
       * &"fontname"   Selects the named font
       * &nn   Selects the specified 2-digit font point size
    """
    CENTER = 'C'
    LEFT = 'L'
    RIGHT = 'R'

    REPLACE_LIST = (
        ('\n', '_x000D_'),
        ('&[Page]', '&P'),
        ('&[Pages]', '&N'),
        ('&[Date]', '&D'),
        ('&[Time]', '&T'),
        ('&[Path]', '&Z'),
        ('&[File]', '&F'),
        ('&[Tab]', '&A'),
        ('&[Picture]', '&G')
        )

    __slots__ = ('type',
                 'font_name',
                 'font_size',
                 'font_color',
                 'text')

    def __init__(self, type):
        self.type = type
        self.font_name = "Calibri,Regular"
        self.font_size = None
        self.font_color = "000000"
        self.text = None

    def has(self):
        return True if self.text else False

    def get(self):
        t = []
        if self.text:
            t.append('&%s' % self.type)
            t.append('&"%s"' % self.font_name)
            if self.font_size:
                t.append('&%d' % self.font_size)
            t.append('&K%s' % self.font_color)
            text = self.text
            for old, new in self.REPLACE_LIST:
                text = text.replace(old, new)
            t.append(text)
        return ''.join(t)

    def set(self, itemArray):
        textArray = []
        for item in itemArray[1:]:
            if len(item) and textArray:
                textArray.append('&%s' % item)
            elif len(item) and not textArray:
                if item[0] == '"':
                    self.font_name = item.replace('"', '')
                elif item[0] == 'K':
                    self.font_color = item[1:7]
                    textArray.append(item[7:])
                else:
                    try:
                        self.font_size = int(item)
                    except:
                        pass
        self.text = ''.join(textArray)

class HeaderFooter(object):
    """Information about the header/footer for this sheet.
    """
    __slots__ = ('left_header',
                 'center_header',
                 'right_header',
                 'left_footer',
                 'center_footer',
                 'right_footer')

    def __init__(self):
        self.left_header = HeaderFooterItem(HeaderFooterItem.LEFT)
        self.center_header = HeaderFooterItem(HeaderFooterItem.CENTER)
        self.right_header = HeaderFooterItem(HeaderFooterItem.RIGHT)
        self.left_footer = HeaderFooterItem(HeaderFooterItem.LEFT)
        self.center_footer = HeaderFooterItem(HeaderFooterItem.CENTER)
        self.right_footer = HeaderFooterItem(HeaderFooterItem.RIGHT)

    def hasHeader(self):
        return True if self.left_header.has() or self.center_header.has() or self.right_header.has() else False

    def hasFooter(self):
        return True if self.left_footer.has() or self.center_footer.has() or self.right_footer.has() else False

    def getHeader(self):
        t = []
        if self.left_header.has():
            t.append(self.left_header.get())
        if self.center_header.has():
            t.append(self.center_header.get())
        if self.right_header.has():
            t.append(self.right_header.get())
        return ''.join(t)

    def getFooter(self):
        t = []
        if self.left_footer.has():
            t.append(self.left_footer.get())
        if self.center_footer.has():
            t.append(self.center_footer.get())
        if self.right_footer.has():
            t.append(self.right_footer.get())
        return ''.join(t)

    def setHeader(self, item):
        itemArray = [i.replace('#DOUBLEAMP#', '&&') for i in item.replace('&&', '#DOUBLEAMP#').split('&')]
        l = itemArray.index('L') if 'L' in itemArray else None
        c = itemArray.index('C') if 'C' in itemArray else None
        r = itemArray.index('R') if 'R' in itemArray else None
        if l:
            if c:
                self.left_header.set(itemArray[l:c])
            elif r:
                self.left_header.set(itemArray[l:r])
            else:
                self.left_header.set(itemArray[l:])
        if c:
            if r:
                self.center_header.set(itemArray[c:r])
            else:
                self.center_header.set(itemArray[c:])
        if r:
            self.right_header.set(itemArray[r:])

    def setFooter(self, item):
        itemArray = [i.replace('#DOUBLEAMP#', '&&') for i in item.replace('&&', '#DOUBLEAMP#').split('&')]
        l = itemArray.index('L') if 'L' in itemArray else None
        c = itemArray.index('C') if 'C' in itemArray else None
        r = itemArray.index('R') if 'R' in itemArray else None
        if l:
            if c:
                self.left_footer.set(itemArray[l:c])
            elif r:
                self.left_footer.set(itemArray[l:r])
            else:
                self.left_footer.set(itemArray[l:])
        if c:
            if r:
                self.center_footer.set(itemArray[c:r])
            else:
                self.center_footer.set(itemArray[c:])
        if r:
            self.right_footer.set(itemArray[r:])

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

    def __init__(self, index=0):
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

    def __init__(self, index='A'):
        self.column_index = index
        self.width = -1
        self.auto_size = False
        self.visible = True
        self.outline_level = 0
        self.collapsed = False
        self.style_index = 0

class PageMargins(object):
    """Information about page margins for view/print layouts."""

    valid_margins = ("left", "right", "top", "bottom", "header", "footer")

    def __init__(self):
        self.left = self.right = self.top = self.bottom = self.header = self.footer = None

    @property
    def margins(self):
        margins = OrderedDict()
        for margin_name in self.valid_margins:
            margin_value = getattr(self, margin_name)
            if margin_value:
                margins[margin_name] = "%0.2f" % margin_value

        return margins

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

    def set_password(self, value='', already_hashed=False):
        """Set a password on this sheet."""
        if not already_hashed:
            value = hash_password(value)
        self._password = value

    def _set_raw_password(self, value):
        """Set a password directly, forcing a hash step."""
        self.set_password(value, already_hashed=False)

    def _get_raw_password(self):
        """Return the password value, regardless of hash."""
        return self._password

    password = property(_get_raw_password, _set_raw_password,
            'get/set the password (if already hashed, '
            'use set_password() instead)')


class Worksheet(object):
    """Represents a worksheet.

    Do not create worksheets yourself,
    use :func:`openpyxl.workbook.Workbook.create_sheet` instead

    """
    repr_format = unicode('<Worksheet "%s">')

    BREAK_NONE = 0
    BREAK_ROW = 1
    BREAK_COLUMN = 2

    SHEETSTATE_VISIBLE = 'visible'
    SHEETSTATE_HIDDEN = 'hidden'
    SHEETSTATE_VERYHIDDEN = 'veryHidden'

    # Paper size
    PAPERSIZE_LETTER = '1'
    PAPERSIZE_LETTER_SMALL = '2'
    PAPERSIZE_TABLOID = '3'
    PAPERSIZE_LEDGER = '4'
    PAPERSIZE_LEGAL = '5'
    PAPERSIZE_STATEMENT = '6'
    PAPERSIZE_EXECUTIVE = '7'
    PAPERSIZE_A3 = '8'
    PAPERSIZE_A4 = '9'
    PAPERSIZE_A4_SMALL = '10'
    PAPERSIZE_A5 = '11'

    # Page orientation
    ORIENTATION_PORTRAIT = 'portrait'
    ORIENTATION_LANDSCAPE = 'landscape'

    def __init__(self, parent_workbook, title='Sheet'):
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
        self._images = []
        self._merged_cells = []
        self.relationships = []
        self._data_validations = []
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
        self.paper_size = None
        self.orientation = None

    def __repr__(self):
        return self.repr_format % self.title

    @property
    def parent(self):
        return self._parent

    @property
    def encoding(self):
        return self._parent.encoding

    def garbage_collect(self):
        """Delete cells that are not storing a value."""
        delete_list = [coordinate for coordinate, cell in \
            iteritems(self._cells) if (not cell.merged and cell.value in ('', None) and \
            (coordinate not in self._styles or
            hash(cell.style) == _DEFAULTS_STYLE_HASH))]
        for coordinate in delete_list:
            del self._cells[coordinate]

    def get_cell_collection(self):
        """Return an unordered list of the cells in this worksheet."""
        return self._cells.values()

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

    title = property(_get_title, _set_title, doc=
                     'Get or set the title of the worksheet. '
                     'Limited to 31 characters, no special characters.')

    def _set_auto_filter(self, range):
        # Normalize range to a str or None
        if not range:
            range = None
        elif isinstance(range, str):
            range = range.upper()
        else:  # Assume a range
            range = range[0][0].address + ':' + range[-1][-1].address
        self._auto_filter = range

    def _get_auto_filter(self):
        return self._auto_filter

    auto_filter = property(_get_auto_filter, _set_auto_filter, doc=
                           'get or set auto filtering on columns')
    def _set_freeze_panes(self, topLeftCell):
        if not topLeftCell:
            topLeftCell = None
        elif isinstance(topLeftCell, str):
            topLeftCell = topLeftCell.upper()
        else:  # Assume a cell
            topLeftCell = topLeftCell.address
        if topLeftCell == 'A1':
            topLeftCell = None
        self._freeze_panes = topLeftCell

    def _get_freeze_panes(self):
        return self._freeze_panes

    freeze_panes = property(_get_freeze_panes, _set_freeze_panes, doc=
                           "Get or set frozen panes")

    def cell(self, coordinate=None, row=None, column=None):
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

        :rtype: :class:`openpyxl.cell.Cell`

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
            new_cell = openpyxl.cell.Cell(self, column, row)
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

    def range(self, range_string, row=0, column=0):
        """Returns a 2D array of cells, with optional row and column offsets.

        :param range_string: cell range string or `named range` name
        :type range_string: string

        :param row: number of rows to offset
        :type row: int

        :param column: number of columns to offset
        :type column: int

        :rtype: tuples of tuples of :class:`openpyxl.cell.Cell`

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
            for col in xrange(min_col, max_col + 1):
                cache_cols[col] = get_column_letter(col)
            rows = xrange(min_row + row, max_row + row + 1)
            cols = xrange(min_col, max_col + 1)
            for row in rows:
                new_row = []
                for col in cols:
                    new_row.append(self.cell('%s%s' % (cache_cols[col], row)))
                result.append(tuple(new_row))
            return tuple(result)
        else:
            try:
                return self.cell(coordinate=range_string, row=row,
                        column=column)
            except CellCoordinatesException:
                pass

            # named range
            named_range = self._parent.get_named_range(range_string)
            if named_range is None:
                msg = '%s is not a valid range name' % range_string
                raise NamedRangeException(msg)
            if isinstance(named_range, NamedRangeContainingValue):
                msg = '%s refers to a value, not a range' % range_string
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

    def set_printer_settings(self, paper_size, orientation):
        """Set printer settings """

        self.paper_size = paper_size
        assert orientation in (self.ORIENTATION_PORTRAIT, self.ORIENTATION_LANDSCAPE), "Values should be %s or %s" % (self.ORIENTATION_PORTRAIT, self.ORIENTATION_LANDSCAPE)
        self.orientation = orientation

    def create_relationship(self, rel_type):
        """Add a relationship for this sheet."""
        rel = Relationship(rel_type)
        self.relationships.append(rel)
        rel_id = self.relationships.index(rel)
        rel.id = 'rId' + str(rel_id + 1)
        return self.relationships[rel_id]

    def add_data_validation(self, data_validation):
        """ Add a data-validation object to the sheet.  The data-validation
            object defines the type of data-validation to be applied and the
            cell or range of cells it should apply to.
        """
        data_validation._sheet = self
        self._data_validations.append(data_validation)
                
    def add_chart(self, chart):
        """ Add a chart to the sheet """

        chart._sheet = self
        self._charts.append(chart)

    def add_image(self, img):
        """ Add an image to the sheet """

        img._sheet = self
        self._images.append(img)

    def merge_cells(self, range_string=None, start_row=None, start_column=None, end_row=None, end_column=None):
        """ Set merge on a cell range.  Range is a cell range (e.g. A1:E1) """
        if not range_string:
            if  start_row is None or start_column is None or end_row is None or end_column is None:
                msg = "You have to provide a value either for "\
                      "'coordinate' or for 'start_row', 'start_column', 'end_row' *and* 'end_column'"
                raise InsufficientCoordinatesException(msg)
            else:
                range_string = '%s%s:%s%s' % (get_column_letter(start_column + 1), start_row + 1, get_column_letter(end_column + 1), end_row + 1)
        elif len(range_string.split(':')) != 2:
                msg = "Range must be a cell range (e.g. A1:E1)"
                raise InsufficientCoordinatesException(msg)
        else:
            range_string = range_string.replace('$', '')

        # Make sure top_left cell exists - is this necessary?
        min_col, min_row = coordinate_from_string(range_string.split(':')[0])
        max_col, max_row = coordinate_from_string(range_string.split(':')[1])
        min_col = column_index_from_string(min_col)
        max_col = column_index_from_string(max_col)
        # Blank out the rest of the cells in the range
        for col in xrange(min_col, max_col + 1):
            for row in xrange(min_row, max_row + 1):
                if not (row == min_row and col == min_col):
                    # PHPExcel adds cell and specifically blanks it out if it doesn't exist
                    self._get_cell('%s%s' % (get_column_letter(col), row)).value = None
                    self._get_cell('%s%s' % (get_column_letter(col), row)).merged = True

        if range_string not in self._merged_cells:
            self._merged_cells.append(range_string)

    def unmerge_cells(self, range_string=None, start_row=None, start_column=None, end_row=None, end_column=None):
        """ Remove merge on a cell range.  Range is a cell range (e.g. A1:E1) """
        if not range_string:
            if start_row is None or start_column is None or end_row is None or end_column is None:
                msg = "You have to provide a value either for "\
                      "'coordinate' or for 'start_row', 'start_column', 'end_row' *and* 'end_column'"
                raise InsufficientCoordinatesException(msg)
            else:
                range_string = '%s%s:%s%s' % (get_column_letter(start_column + 1), start_row + 1, get_column_letter(end_column + 1), end_row + 1)
        elif len(range_string.split(':')) != 2:
            msg = "Range must be a cell range (e.g. A1:E1)"
            raise InsufficientCoordinatesException(msg)
        else:
            range_string = range_string.replace('$', '')

        if range_string in self._merged_cells:
            self._merged_cells.remove(range_string)
            min_col, min_row = coordinate_from_string(range_string.split(':')[0])
            max_col, max_row = coordinate_from_string(range_string.split(':')[1])
            min_col = column_index_from_string(min_col)
            max_col = column_index_from_string(max_col)
            # Mark cell as unmerged
            for col in xrange(min_col, max_col + 1):
                for row in xrange(min_row, max_row + 1):
                    if not (row == min_row and col == min_col):
                        self._get_cell('%s%s' % (get_column_letter(col), row)).merged = False
        else:
            msg = 'Cell range %s not known as merged.' % range_string
            raise InsufficientCoordinatesException(msg)

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
                self.cell(row=row_idx, column=col_idx).value = content

        elif isinstance(list_or_dict, dict):
            for col_idx, content in iteritems(list_or_dict):
                if isinstance(col_idx, basestring):
                    col_idx = column_index_from_string(col_idx) - 1
                self.cell(row=row_idx, column=col_idx).value = content

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
            col = get_column_letter(col_idx + 1)
            res = self.range('%s1:%s%d' % (col, col, max_row))
            cols.append(tuple([x[0] for x in res]))

        return tuple(cols)

    def point_pos(self, left=0, top=0):
        """ tells which cell is under the given coordinates (in pixels)
        counting from the top-left corner of the sheet.
        Can be used to locate images and charts on the worksheet """
        current_col = 1
        current_row = 1
        column_dimensions = self.column_dimensions
        row_dimensions = self.row_dimensions
        default_width = points_to_pixels(DEFAULT_COLUMN_WIDTH)
        default_height = points_to_pixels(DEFAULT_ROW_HEIGHT)
        left_pos = 0
        top_pos = 0

        while left_pos <= left:
            letter = get_column_letter(current_col)
            current_col += 1
            if letter in column_dimensions:
                cdw = column_dimensions[letter].width
                if cdw > 0:
                    left_pos += points_to_pixels(cdw)
                    continue
            left_pos += default_width

        while top_pos <= top:
            row = current_row
            current_row += 1
            if row in row_dimensions:
                rdh = row_dimensions[row].height
                if rdh > 0:
                    top_pos += points_to_pixels(rdh)
                    continue
            top_pos += default_height

        return (letter, row)

