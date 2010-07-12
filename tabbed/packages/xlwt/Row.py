# -*- coding: windows-1252 -*-

import BIFFRecords
import Style
from Cell import StrCell, BlankCell, NumberCell, FormulaCell, MulBlankCell, BooleanCell, ErrorCell, \
    _get_cells_biff_data_mul
import ExcelFormula
import datetime as dt
try:
    from decimal import Decimal
except ImportError:
    # Python 2.3: decimal not supported; create dummy Decimal class
    class Decimal(object):
        pass


class Row(object):
    __slots__ = [# private variables
                 "__idx",
                 "__parent",
                 "__parent_wb",
                 "__cells",
                 "__min_col_idx",
                 "__max_col_idx",
                 "__xf_index",
                 "__has_default_xf_index",
                 "__height_in_pixels",
                 # public variables
                 "height",
                 "has_default_height",
                 "height_mismatch",
                 "level",
                 "collapse",
                 "hidden",
                 "space_above",
                 "space_below"]

    def __init__(self, rowx, parent_sheet):
        if not (isinstance(rowx, int) and 0 <= rowx <= 65535):
            raise ValueError("row index (%r) not an int in range(65536)" % rowx)
        self.__idx = rowx
        self.__parent = parent_sheet
        self.__parent_wb = parent_sheet.get_parent()
        self.__cells = {}
        self.__min_col_idx = 0
        self.__max_col_idx = 0
        self.__xf_index = 0x0F
        self.__has_default_xf_index = 0
        self.__height_in_pixels = 0x11

        self.height = 0x00FF
        self.has_default_height = 0x00
        self.height_mismatch = 0
        self.level = 0
        self.collapse = 0
        self.hidden = 0
        self.space_above = 0
        self.space_below = 0


    def __adjust_height(self, style):
        twips = style.font.height
        points = float(twips)/20.0
        # Cell height in pixels can be calcuted by following approx. formula:
        # cell height in pixels = font height in points * 83/50 + 2/5
        # It works when screen resolution is 96 dpi
        pix = int(round(points*83.0/50.0 + 2.0/5.0))
        if pix > self.__height_in_pixels:
            self.__height_in_pixels = pix


    def __adjust_bound_col_idx(self, *args):
        for arg in args:
            iarg = int(arg)
            if not ((0 <= iarg <= 255) and arg == iarg):
                raise ValueError("column index (%r) not an int in range(256)" % arg)
            sheet = self.__parent
            if iarg < self.__min_col_idx:
                self.__min_col_idx = iarg
            if iarg > self.__max_col_idx:
                self.__max_col_idx = iarg
            if iarg < sheet.first_used_col:
                sheet.first_used_col = iarg
            if iarg > sheet.last_used_col:
                sheet.last_used_col = iarg

    def __excel_date_dt(self, date):
        if isinstance(date, dt.date) and (not isinstance(date, dt.datetime)):
            epoch = dt.date(1899, 12, 31)
        elif isinstance(date, dt.time):
            date = dt.datetime.combine(dt.datetime(1900, 1, 1), date)
            epoch = dt.datetime(1900, 1, 1, 0, 0, 0)
        else:
            epoch = dt.datetime(1899, 12, 31, 0, 0, 0)
        delta = date - epoch
        xldate = delta.days + float(delta.seconds) / (24*60*60)
        # Add a day for Excel's missing leap day in 1900
        if xldate > 59:
            xldate += 1
        return xldate

    def get_height_in_pixels(self):
        return self.__height_in_pixels


    def set_style(self, style):
        self.__adjust_height(style)
        self.__xf_index = self.__parent_wb.add_style(style)
        self.__has_default_xf_index = 1


    def get_xf_index(self):
        return self.__xf_index


    def get_cells_count(self):
        return len(self.__cells)


    def get_min_col(self):
        return self.__min_col_idx


    def get_max_col(self):
        return self.__max_col_idx


    def get_row_biff_data(self):
        height_options = (self.height & 0x07FFF)
        height_options |= (self.has_default_height & 0x01) << 15

        options =  (self.level & 0x07) << 0
        options |= (self.collapse & 0x01) << 4
        options |= (self.hidden & 0x01) << 5
        options |= (self.height_mismatch & 0x01) << 6
        options |= (self.__has_default_xf_index & 0x01) << 7
        options |= (0x01 & 0x01) << 8
        options |= (self.__xf_index & 0x0FFF) << 16
        options |= (self.space_above & 1) << 28
        options |= (self.space_below & 1) << 29

        return BIFFRecords.RowRecord(self.__idx, self.__min_col_idx,
            self.__max_col_idx, height_options, options).get()

    def insert_cell(self, col_index, cell_obj):
        if col_index in self.__cells:
            if not self.__parent._cell_overwrite_ok:
                msg = "Attempt to overwrite cell: sheetname=%r rowx=%d colx=%d" \
                    % (self.__parent.name, self.__idx, col_index)
                raise Exception(msg)
            prev_cell_obj = self.__cells[col_index]
            sst_idx = getattr(prev_cell_obj, 'sst_idx', None)
            if sst_idx is not None:
                self.__parent_wb.del_str(sst_idx)
        self.__cells[col_index] = cell_obj

    def insert_mulcells(self, colx1, colx2, cell_obj):
        self.insert_cell(colx1, cell_obj)
        for col_index in xrange(colx1+1, colx2+1):
            self.insert_cell(col_index, None)

    def get_cells_biff_data(self):
        cell_items = [item for item in self.__cells.iteritems() if item[1] is not None]
        cell_items.sort() # in column order
        return _get_cells_biff_data_mul(self.__idx, cell_items)
        # previously:
        # return ''.join([cell.get_biff_data() for colx, cell in cell_items])

    def get_index(self):
        return self.__idx

    def set_cell_text(self, colx, value, style=Style.default_style):
        self.__adjust_height(style)
        self.__adjust_bound_col_idx(colx)
        xf_index = self.__parent_wb.add_style(style)
        self.insert_cell(colx, StrCell(self.__idx, colx, xf_index, self.__parent_wb.add_str(value)))

    def set_cell_blank(self, colx, style=Style.default_style):
        self.__adjust_height(style)
        self.__adjust_bound_col_idx(colx)
        xf_index = self.__parent_wb.add_style(style)
        self.insert_cell(colx, BlankCell(self.__idx, colx, xf_index))

    def set_cell_mulblanks(self, first_colx, last_colx, style=Style.default_style):
        assert 0 <= first_colx <= last_colx <= 255
        self.__adjust_height(style)
        self.__adjust_bound_col_idx(first_colx, last_colx)
        xf_index = self.__parent_wb.add_style(style)
        # ncols = last_colx - first_colx + 1
        self.insert_mulcells(first_colx, last_colx, MulBlankCell(self.__idx, first_colx, last_colx, xf_index))

    def set_cell_number(self, colx, number, style=Style.default_style):
        self.__adjust_height(style)
        self.__adjust_bound_col_idx(colx)
        xf_index = self.__parent_wb.add_style(style)
        self.insert_cell(colx, NumberCell(self.__idx, colx, xf_index, number))

    def set_cell_date(self, colx, datetime_obj, style=Style.default_style):
        self.__adjust_height(style)
        self.__adjust_bound_col_idx(colx)
        xf_index = self.__parent_wb.add_style(style)
        self.insert_cell(colx,
            NumberCell(self.__idx, colx, xf_index, self.__excel_date_dt(datetime_obj)))

    def set_cell_formula(self, colx, formula, style=Style.default_style, calc_flags=0):
        self.__adjust_height(style)
        self.__adjust_bound_col_idx(colx)
        xf_index = self.__parent_wb.add_style(style)
        self.__parent_wb.add_sheet_reference(formula)
        self.insert_cell(colx, FormulaCell(self.__idx, colx, xf_index, formula, calc_flags=0))

    def set_cell_boolean(self, colx, value, style=Style.default_style):
        self.__adjust_height(style)
        self.__adjust_bound_col_idx(colx)
        xf_index = self.__parent_wb.add_style(style)
        self.insert_cell(colx, BooleanCell(self.__idx, colx, xf_index, bool(value)))

    def set_cell_error(self, colx, error_string_or_code, style=Style.default_style):
        self.__adjust_height(style)
        self.__adjust_bound_col_idx(colx)
        xf_index = self.__parent_wb.add_style(style)
        self.insert_cell(colx, ErrorCell(self.__idx, colx, xf_index, error_string_or_code))

    def write(self, col, label, style=Style.default_style):
        self.__adjust_height(style)
        self.__adjust_bound_col_idx(col)
        style_index = self.__parent_wb.add_style(style)
        if isinstance(label, basestring):
            if len(label) > 0:
                self.insert_cell(col,
                    StrCell(self.__idx, col, style_index, self.__parent_wb.add_str(label))
                    )
            else:
                self.insert_cell(col, BlankCell(self.__idx, col, style_index))
        elif isinstance(label, bool): # bool is subclass of int; test bool first
            self.insert_cell(col, BooleanCell(self.__idx, col, style_index, label))
        elif isinstance(label, (float, int, long, Decimal)):
            self.insert_cell(col, NumberCell(self.__idx, col, style_index, label))
        elif isinstance(label, (dt.datetime, dt.date, dt.time)):
            date_number = self.__excel_date_dt(label)
            self.insert_cell(col, NumberCell(self.__idx, col, style_index, date_number))
        elif label is None:
            self.insert_cell(col, BlankCell(self.__idx, col, style_index))
        elif isinstance(label, ExcelFormula.Formula):
            self.__parent_wb.add_sheet_reference(label)
            self.insert_cell(col, FormulaCell(self.__idx, col, style_index, label))
        else:
            raise Exception("Unexpected data type %r" % type(label))

    write_blanks = set_cell_mulblanks



