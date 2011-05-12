# file openpyxl/style.py

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

"""Style and formatting option tracking."""

# Python stdlib imports
import re
try:
    from hashlib import md5
except ImportError:
    from md5 import md5


class HashableObject(object):
    """Define how to hash property classes."""
    __fields__ = None
    __leaf__ = False

    def __repr__(self):

        return ':'.join([repr(getattr(self, x)) for x in self.__fields__])

    def __hash__(self):

#        return int(md5(repr(self)).hexdigest(), 16)
        return hash(repr(self))

class Color(HashableObject):
    """Named colors for use in styles."""
    BLACK = 'FF000000'
    WHITE = 'FFFFFFFF'
    RED = 'FFFF0000'
    DARKRED = 'FF800000'
    BLUE = 'FF0000FF'
    DARKBLUE = 'FF000080'
    GREEN = 'FF00FF00'
    DARKGREEN = 'FF008000'
    YELLOW = 'FFFFFF00'
    DARKYELLOW = 'FF808000'

    __fields__ = ('index',)
    __slots__ = __fields__
    __leaf__ = True

    def __init__(self, index):
        super(Color, self).__init__()
        self.index = index


class Font(HashableObject):
    """Font options used in styles."""
    UNDERLINE_NONE = 'none'
    UNDERLINE_DOUBLE = 'double'
    UNDERLINE_DOUBLE_ACCOUNTING = 'doubleAccounting'
    UNDERLINE_SINGLE = 'single'
    UNDERLINE_SINGLE_ACCOUNTING = 'singleAccounting'

    __fields__ = ('name',
                  'size',
                  'bold',
                  'italic',
                  'superscript',
                  'subscript',
                  'underline',
                  'strikethrough',
                  'color')
    __slots__ = __fields__

    def __init__(self):
        super(Font, self).__init__()
        self.name = 'Calibri'
        self.size = 11
        self.bold = False
        self.italic = False
        self.superscript = False
        self.subscript = False
        self.underline = self.UNDERLINE_NONE
        self.strikethrough = False
        self.color = Color(Color.BLACK)


class Fill(HashableObject):
    """Area fill patterns for use in styles."""
    FILL_NONE = 'none'
    FILL_SOLID = 'solid'
    FILL_GRADIENT_LINEAR = 'linear'
    FILL_GRADIENT_PATH = 'path'
    FILL_PATTERN_DARKDOWN = 'darkDown'
    FILL_PATTERN_DARKGRAY = 'darkGray'
    FILL_PATTERN_DARKGRID = 'darkGrid'
    FILL_PATTERN_DARKHORIZONTAL = 'darkHorizontal'
    FILL_PATTERN_DARKTRELLIS = 'darkTrellis'
    FILL_PATTERN_DARKUP = 'darkUp'
    FILL_PATTERN_DARKVERTICAL = 'darkVertical'
    FILL_PATTERN_GRAY0625 = 'gray0625'
    FILL_PATTERN_GRAY125 = 'gray125'
    FILL_PATTERN_LIGHTDOWN = 'lightDown'
    FILL_PATTERN_LIGHTGRAY = 'lightGray'
    FILL_PATTERN_LIGHTGRID = 'lightGrid'
    FILL_PATTERN_LIGHTHORIZONTAL = 'lightHorizontal'
    FILL_PATTERN_LIGHTTRELLIS = 'lightTrellis'
    FILL_PATTERN_LIGHTUP = 'lightUp'
    FILL_PATTERN_LIGHTVERTICAL = 'lightVertical'
    FILL_PATTERN_MEDIUMGRAY = 'mediumGray'

    __fields__ = ('fill_type',
                  'rotation',
                  'start_color',
                  'end_color')
    __slots__ = __fields__

    def __init__(self):
        super(Fill, self).__init__()
        self.fill_type = self.FILL_NONE
        self.rotation = 0
        self.start_color = Color(Color.WHITE)
        self.end_color = Color(Color.BLACK)


class Border(HashableObject):
    """Border options for use in styles."""
    BORDER_NONE = 'none'
    BORDER_DASHDOT = 'dashDot'
    BORDER_DASHDOTDOT = 'dashDotDot'
    BORDER_DASHED = 'dashed'
    BORDER_DOTTED = 'dotted'
    BORDER_DOUBLE = 'double'
    BORDER_HAIR = 'hair'
    BORDER_MEDIUM = 'medium'
    BORDER_MEDIUMDASHDOT = 'mediumDashDot'
    BORDER_MEDIUMDASHDOTDOT = 'mediumDashDotDot'
    BORDER_MEDIUMDASHED = 'mediumDashed'
    BORDER_SLANTDASHDOT = 'slantDashDot'
    BORDER_THICK = 'thick'
    BORDER_THIN = 'thin'

    __fields__ = ('border_style',
                  'color')
    __slots__ = __fields__

    def __init__(self):
        super(Border, self).__init__()
        self.border_style = self.BORDER_NONE
        self.color = Color(Color.BLACK)


class Borders(HashableObject):
    """Border positioning for use in styles."""
    DIAGONAL_NONE = 0
    DIAGONAL_UP = 1
    DIAGONAL_DOWN = 2
    DIAGONAL_BOTH = 3

    __fields__ = ('left',
                  'right',
                  'top',
                  'bottom',
                  'diagonal',
                  'diagonal_direction',
                  'all_borders',
                  'outline',
                  'inside',
                  'vertical',
                  'horizontal')
    __slots__ = __fields__

    def __init__(self):
        super(Borders, self).__init__()
        self.left = Border()
        self.right = Border()
        self.top = Border()
        self.bottom = Border()
        self.diagonal = Border()
        self.diagonal_direction = self.DIAGONAL_NONE

        self.all_borders = Border()
        self.outline = Border()
        self.inside = Border()
        self.vertical = Border()
        self.horizontal = Border()


class Alignment(HashableObject):
    """Alignment options for use in styles."""
    HORIZONTAL_GENERAL = 'general'
    HORIZONTAL_LEFT = 'left'
    HORIZONTAL_RIGHT = 'right'
    HORIZONTAL_CENTER = 'center'
    HORIZONTAL_CENTER_CONTINUOUS = 'centerContinuous'
    HORIZONTAL_JUSTIFY = 'justify'
    VERTICAL_BOTTOM = 'bottom'
    VERTICAL_TOP = 'top'
    VERTICAL_CENTER = 'center'
    VERTICAL_JUSTIFY = 'justify'

    __fields__ = ('horizontal',
                  'vertical',
                  'text_rotation',
                  'wrap_text',
                  'shrink_to_fit',
                  'indent')
    __slots__ = __fields__
    __leaf__ = True

    def __init__(self):
        super(Alignment, self).__init__()
        self.horizontal = self.HORIZONTAL_GENERAL
        self.vertical = self.VERTICAL_BOTTOM
        self.text_rotation = 0
        self.wrap_text = False
        self.shrink_to_fit = False
        self.indent = 0


class NumberFormat(HashableObject):
    """Numer formatting for use in styles."""
    FORMAT_GENERAL = 'General'
    FORMAT_TEXT = '@'
    FORMAT_NUMBER = '0'
    FORMAT_NUMBER_00 = '0.00'
    FORMAT_NUMBER_COMMA_SEPARATED1 = '#,##0.00'
    FORMAT_NUMBER_COMMA_SEPARATED2 = '#,##0.00_-'
    FORMAT_PERCENTAGE = '0%'
    FORMAT_PERCENTAGE_00 = '0.00%'
    FORMAT_DATE_YYYYMMDD2 = 'yyyy-mm-dd'
    FORMAT_DATE_YYYYMMDD = 'yy-mm-dd'
    FORMAT_DATE_DDMMYYYY = 'dd/mm/yy'
    FORMAT_DATE_DMYSLASH = 'd/m/y'
    FORMAT_DATE_DMYMINUS = 'd-m-y'
    FORMAT_DATE_DMMINUS = 'd-m'
    FORMAT_DATE_MYMINUS = 'm-y'
    FORMAT_DATE_XLSX14 = 'mm-dd-yy'
    FORMAT_DATE_XLSX15 = 'd-mmm-yy'
    FORMAT_DATE_XLSX16 = 'd-mmm'
    FORMAT_DATE_XLSX17 = 'mmm-yy'
    FORMAT_DATE_XLSX22 = 'm/d/yy h:mm'
    FORMAT_DATE_DATETIME = 'd/m/y h:mm'
    FORMAT_DATE_TIME1 = 'h:mm AM/PM'
    FORMAT_DATE_TIME2 = 'h:mm:ss AM/PM'
    FORMAT_DATE_TIME3 = 'h:mm'
    FORMAT_DATE_TIME4 = 'h:mm:ss'
    FORMAT_DATE_TIME5 = 'mm:ss'
    FORMAT_DATE_TIME6 = 'h:mm:ss'
    FORMAT_DATE_TIME7 = 'i:s.S'
    FORMAT_DATE_TIME8 = 'h:mm:ss@'
    FORMAT_DATE_YYYYMMDDSLASH = 'yy/mm/dd@'
    FORMAT_CURRENCY_USD_SIMPLE = '"$"#,##0.00_-'
    FORMAT_CURRENCY_USD = '$#,##0_-'
    FORMAT_CURRENCY_EUR_SIMPLE = '[$EUR ]#,##0.00_-'
    _BUILTIN_FORMATS = {
        0: 'General',
        1: '0',
        2: '0.00',
        3: '#,##0',
        4: '#,##0.00',

        9: '0%',
        10: '0.00%',
        11: '0.00E+00',
        12: '# ?/?',
        13: '# ??/??',
        14: 'mm-dd-yy',
        15: 'd-mmm-yy',
        16: 'd-mmm',
        17: 'mmm-yy',
        18: 'h:mm AM/PM',
        19: 'h:mm:ss AM/PM',
        20: 'h:mm',
        21: 'h:mm:ss',
        22: 'm/d/yy h:mm',

        37: '#,##0 (#,##0)',
        38: '#,##0 [Red](#,##0)',
        39: '#,##0.00(#,##0.00)',
        40: '#,##0.00[Red](#,##0.00)',

        41: '_(* #,##0_);_(* \(#,##0\);_(* "-"_);_(@_)',
        42: '_("$"* #,##0_);_("$"* \(#,##0\);_("$"* "-"_);_(@_)',
        43: '_(* #,##0.00_);_(* \(#,##0.00\);_(* "-"??_);_(@_)',

        44: '_("$"* #,##0.00_)_("$"* \(#,##0.00\)_("$"* "-"??_)_(@_)',
        45: 'mm:ss',
        46: '[h]:mm:ss',
        47: 'mmss.0',
        48: '##0.0E+0',
        49: '@', }
    _BUILTIN_FORMATS_REVERSE = dict(
            [(value, key) for key, value in _BUILTIN_FORMATS.items()])

    __fields__ = ('_format_code',
                  '_format_index')
    __slots__ = __fields__
    __leaf__ = True

    DATE_INDICATORS = 'dmyhs'

    def __init__(self):
        super(NumberFormat, self).__init__()
        self._format_code = self.FORMAT_GENERAL
        self._format_index = 0

    def _set_format_code(self, format_code = FORMAT_GENERAL):
        """Setter for the format_code property."""
        self._format_code = format_code
        self._format_index = self.builtin_format_id(format = format_code)

    def _get_format_code(self):
        """Getter for the format_code property."""
        return self._format_code

    format_code = property(_get_format_code, _set_format_code)

    def builtin_format_code(self, index):
        """Return one of the standard format codes by index."""
        return self._BUILTIN_FORMATS[index]

    def is_builtin(self, format = None):
        """Check if a format code is a standard format code."""
        if format is None:
            format = self._format_code
        return format in self._BUILTIN_FORMATS.values()

    def builtin_format_id(self, format):
        """Return the id of a standard style."""
        return self._BUILTIN_FORMATS_REVERSE.get(format, None)

    def is_date_format(self, format = None):
        """Check if the number format is actually representing a date."""
        if format is None:
            format = self._format_code

        return any([x in format for x in self.DATE_INDICATORS])

class Protection(HashableObject):
    """Protection options for use in styles."""
    PROTECTION_INHERIT = 'inherit'
    PROTECTION_PROTECTED = 'protected'
    PROTECTION_UNPROTECTED = 'unprotected'

    __fields__ = ('locked',
                  'hidden')
    __slots__ = __fields__
    __leaf__ = True

    def __init__(self):
        super(Protection, self).__init__()
        self.locked = self.PROTECTION_INHERIT
        self.hidden = self.PROTECTION_INHERIT


class Style(HashableObject):
    """Style object containing all formatting details."""
    __fields__ = ('font',
                  'fill',
                  'borders',
                  'alignment',
                  'number_format',
                  'protection')
    __slots__ = __fields__

    def __init__(self):
        super(Style, self).__init__()
        self.font = Font()
        self.fill = Fill()
        self.borders = Borders()
        self.alignment = Alignment()
        self.number_format = NumberFormat()
        self.protection = Protection()

DEFAULTS = Style()
