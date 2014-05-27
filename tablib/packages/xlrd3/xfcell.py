# Author:  mozman <mozman@gmx.at>
# Purpose: xfcell -- cell with convenient xf function
# Created: 04.12.2010
# Copyright (C) 2010, Manfred Moitzi
# License: BSD-style licence

"""
The XFCell() object contains the data for one cell.

WARNING: You don't call this class yourself. You access Cell objects
via methods of the Sheet object(s) that you found in the Book object that
was returned when you called xlrd.open_workbook("myfile.xls").

Cell objects have four attributes: `ctype` is an int, `value` (which depends
on `ctype`), `xf_index` and `sheet`, a reference to the containing sheet. If
**formatting_info** is not enabled when the workbook is opened, xf_index will
be **None**.

The following table describes the types of cells and how their values
are represented in Python.

=============== ===== ============ ==========================================
Type symbol     Const Python value Note
=============== ===== ============ ==========================================
XL_CELL_EMPTY   0     ""
XL_CELL_TEXT    1     str
XL_CELL_NUMBER  2     float
XL_CELL_DATE    3     float
XL_CELL_BOOLEAN 4     int          1 means TRUE, 0 means FALSE
XL_CELL_ERROR   5     int          representing internal Excel codes; for a
                                   text representation, refer to the supplied
                                   dictionary error_text_from_code
XL_CELL_BLANK   6     ""           this type will appear only when
                                   open_workbook(..., formatting_info=True)
                                   is used.
=============== ===== ============ ==========================================
"""

import datetime

from .xldate import xldate_as_tuple
from .biffh import XL_CELL_DATE, BaseObject

class XFCell(BaseObject):
    """ Extended Cell() class with convenient methods for easy access of cell
    properties.
    """
    __slots__ = ['sheet', 'ctype', 'value', 'xf']

    def __init__(self, ctype, value, xf_index=None, sheet=None):
        self.sheet = sheet
        self.ctype = ctype
        self.value = value

        if xf_index is not None:
            self.xf = self.book.xf_list[xf_index]
        else:
            self.xf = None

    @property
    def book(self):
        return self.sheet.book

    @property
    def has_xf(self):
        return (self.xf is not None)

    @property
    def xf_index(self):
        if self.has_xf:
            return self.xf.xf_index
        else:
            return None

    @property
    def parent_style(self):
        return self.book.xf_list[self.xf.parent_style_index]

    @property
    def is_datetime(self):
        return self.ctype == XL_CELL_DATE

    @property
    def has_date(self):
        if self.is_datetime:
            return self.value > 1.
        return False

    def get_color(self, index):
        return self.book.colour_map[index]

    def datetime(self):
        """ Returns a datetime.datetime object if cell type is XL_CELL_DATE
        else raises a TypeError, and raises ValueError if the the cell has
        not date value (only time value is present).
        """
        if self.is_datetime:
            if self.has_date:
                date = xldate_as_tuple(self.value, self.book.datemode)
                return datetime.datetime(*date)
            else:
                raise ValueError("Cell has no date value.")
        else:
            raise TypeError("Cell is not a XL_CELL_DATE.")

    def date(self):
        """ Returns a datetime.date object if cell type is XL_CELL_DATE
        else raises a **TypeError**. Raises **ValueError** if the cell
        doesn't have a date value (only time value is present).
        """
        dt = self.datetime()
        return dt.date()

    def time(self):
        """ Returns a datetime.time object if cell type is XL_CELL_DATE else
        raises a TypeError.
        """
        if self.is_datetime:
            date = xldate_as_tuple(self.value, self.book.datemode)
            return datetime.time(date[3], date[4], date[5])
        else:
            raise TypeError("Cell is not a XL_CELL_DATE.")

    #
    # access the XFBackground() class
    #

    @property
    def background(self):
        if self.xf.is_style and \
           self.xf._background_flag == 0:
            return self.xf.background
        elif self.xf._background_flag:
            return self.xf.background
        else:
            return self.parent_style.background

    def background_color(self):
        """ Get cell background-color as 3-tuple. """
        color_index = self.xf.background.background_colour_index
        return self.get_color(color_index)

    def fill_pattern(self):
        return self.xf.background.fill_pattern

    def pattern_color(self):
        color_index = self.xf.background.pattern_colour_index
        return self.get_color(color_index)

    #
    # access the Font() class
    #

    @property
    def font_index(self):
        if self.xf.is_style and \
           self.xf._font_flag == 0:
            return self.xf.font_index
        elif self.xf._font_flag:
            return self.xf.font_index
        else:
            return self.parent_style.font_index

    @property
    def font(self):
        """ Get the Font() class. """
        return self.book.font_list[self.xf.font_index]

    def font_color(self):
        """ Get cell foreground-color as 3-tuple. """
        return self.get_color(self.font.colour_index)

    #
    # access the Format() class
    #

    @property
    def format_key(self):
        if self.xf.is_style and \
           self.xf._format_flag == 0:
            return self.xf.format_key
        elif self.xf._format_flag:
            return self.xf.format_key
        else:
            return self.parent_style.format_key

    @property
    def format(self):
        """ Get the Format() class. """
        return self.book.format_map[self.format_key]

    def format_str(self):
        """ Get the associated 'format_str'. """
        return self.format.format_str

    #
    # access the XFAligment() class
    #

    @property
    def alignment(self):
        if self.xf.is_style and \
           self.xf._alignment_flag == 0:
            return self.xf.alignment
        elif self.xf._alignment_flag:
            return self.xf.alignment
        else:
            return self.parent_style.alignment

    #
    # access the XFBorder() class
    #

    @property
    def border(self):
        if self.xf.is_style and \
           self.xf._border_flag == 0:
            return self.xf.border
        elif self.xf._border_flag:
            return self.xf.border
        else:
            return self.parent_style.border

    def bordercolors(self):
        """ Get border color as dict of rgb-color-tuples. """
        border = self.border
        return {
            'top': self.get_color(border.top_colour_index),
            'bottom': self.get_color(border.bottom_colour_index),
            'left': self.get_color(border.left_colour_index),
            'right': self.get_color(border.right_colour_index),
            'diag': self.get_color(border.diag_colour_index),
        }

    def borderstyles(self):
        """ Get border styles as dict of ints. """
        border = self.border
        return {
            'top': border.top_line_style,
            'bottom': border.bottom_line_style,
            'left': border.left_line_style,
            'right': border.right_line_style,
            'diag': border.diag_line_style,
        }

    @property
    def has_up_diag(self):
        """ Draw a line across the cell from bottom left to top right. """
        return bool(self.border.diag_up)

    @property
    def has_down_diag(self):
        """ Draw a line across the cell from top left to bottom right. """
        return bool(self.border.diag_down)

    #
    # access the XFProtection() class
    #

    @property
    def protection(self):
        if self.xf.is_style and \
           self.xf._protection_flag == 0:
            return self.xf.protection
        elif self.xf._protection_flag:
            return self.xf.protection
        else:
            return self.parent_style.protection

    @property
    def is_cell_locked(self):
        return bool(self.protection.cell_locked)

    @property
    def is_formula_hidden(self):
        return bool(self.protection.cell_locked)
