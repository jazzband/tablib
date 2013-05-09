# file openpyxl/reader/style.py

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

"""Read shared style definitions"""

# package imports
from openpyxl.shared.xmltools import fromstring, QName
from openpyxl.shared.exc import MissingNumberFormat
from openpyxl.style import Style, NumberFormat, Font, Fill, Borders, Protection
from copy import deepcopy


def read_style_table(xml_source):
    """Read styles from the shared style table"""
    table = {}
    xmlns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    root = fromstring(xml_source)
    custom_num_formats = parse_custom_num_formats(root, xmlns)
    color_index = parse_color_index(root, xmlns)
    font_list = parse_fonts(root, xmlns, color_index)
    fill_list = parse_fills(root, xmlns, color_index)
    border_list = parse_borders(root, xmlns, color_index)
    builtin_formats = NumberFormat._BUILTIN_FORMATS
    cell_xfs = root.find(QName(xmlns, 'cellXfs').text)
    if cell_xfs is not None: # can happen on bad OOXML writers (e.g. Gnumeric)
        cell_xfs_nodes = cell_xfs.findall(QName(xmlns, 'xf').text)
        for index, cell_xfs_node in enumerate(cell_xfs_nodes):
            new_style = Style()
            number_format_id = int(cell_xfs_node.get('numFmtId'))
            if number_format_id < 164:
                new_style.number_format.format_code = \
                        builtin_formats.get(number_format_id, 'General')
            else:

                if number_format_id in custom_num_formats:
                    new_style.number_format.format_code = \
                            custom_num_formats[number_format_id]
                else:
                    raise MissingNumberFormat('%s' % number_format_id)

            if cell_xfs_node.get('applyAlignment') == '1':
                alignment = cell_xfs_node.find(QName(xmlns, 'alignment').text)
                if alignment is not None:
                    if alignment.get('horizontal') is not None:
                        new_style.alignment.horizontal = alignment.get('horizontal')
                    if alignment.get('vertical') is not None:
                        new_style.alignment.vertical = alignment.get('vertical')
                    if alignment.get('wrapText'):
                        new_style.alignment.wrap_text = True
                    if alignment.get('shrinkToFit'):
                        new_style.alignment.shrink_to_fit = True
                    if alignment.get('indent') is not None:
                        new_style.alignment.ident = int(alignment.get('indent'))
                    if alignment.get('textRotation') is not None:
                        new_style.alignment.text_rotation = int(alignment.get('textRotation'))
                    # ignore justifyLastLine option when horizontal = distributed

            if cell_xfs_node.get('applyFont') == '1':
                new_style.font = deepcopy(font_list[int(cell_xfs_node.get('fontId'))])
                new_style.font.color = deepcopy(font_list[int(cell_xfs_node.get('fontId'))].color)

            if cell_xfs_node.get('applyFill') == '1':
                new_style.fill = deepcopy(fill_list[int(cell_xfs_node.get('fillId'))])
                new_style.fill.start_color = deepcopy(fill_list[int(cell_xfs_node.get('fillId'))].start_color)
                new_style.fill.end_color = deepcopy(fill_list[int(cell_xfs_node.get('fillId'))].end_color)

            if cell_xfs_node.get('applyBorder') == '1':
                new_style.borders = deepcopy(border_list[int(cell_xfs_node.get('borderId'))])
                new_style.borders.left = deepcopy(border_list[int(cell_xfs_node.get('borderId'))].left)
                new_style.borders.left.color = deepcopy(border_list[int(cell_xfs_node.get('borderId'))].left.color)
                new_style.borders.right = deepcopy(border_list[int(cell_xfs_node.get('borderId'))].right)
                new_style.borders.right.color = deepcopy(border_list[int(cell_xfs_node.get('borderId'))].right.color)
                new_style.borders.top = deepcopy(border_list[int(cell_xfs_node.get('borderId'))].top)
                new_style.borders.top.color = deepcopy(border_list[int(cell_xfs_node.get('borderId'))].top.color)
                new_style.borders.bottom = deepcopy(border_list[int(cell_xfs_node.get('borderId'))].bottom)
                new_style.borders.bottom.color = deepcopy(border_list[int(cell_xfs_node.get('borderId'))].bottom.color)
                new_style.borders.diagonal = deepcopy(border_list[int(cell_xfs_node.get('borderId'))].diagonal)
                new_style.borders.diagonal.color = deepcopy(border_list[int(cell_xfs_node.get('borderId'))].diagonal.color)

            if cell_xfs_node.get('applyProtection') == '1':
                protection = cell_xfs_node.find(QName(xmlns, 'protection').text)
                # Ignore if there are no protection sub-nodes
                if protection is not None:
                    if protection.get('locked') is not None:
                        if protection.get('locked') == '1':
                            new_style.protection.locked = Protection.PROTECTION_PROTECTED
                        else:
                            new_style.protection.locked = Protection.PROTECTION_UNPROTECTED
                    if protection.get('hidden') is not None:
                        if protection.get('hidden') == '1':
                            new_style.protection.hidden = Protection.PROTECTION_PROTECTED
                        else:
                            new_style.protection.hidden = Protection.PROTECTION_UNPROTECTED

            table[index] = new_style
    return table

def parse_custom_num_formats(root, xmlns):
    """Read in custom numeric formatting rules from the shared style table"""
    custom_formats = {}
    num_fmts = root.find(QName(xmlns, 'numFmts').text)
    if num_fmts is not None:
        num_fmt_nodes = num_fmts.findall(QName(xmlns, 'numFmt').text)
        for num_fmt_node in num_fmt_nodes:
            custom_formats[int(num_fmt_node.get('numFmtId'))] = \
                    num_fmt_node.get('formatCode').lower()
    return custom_formats

def parse_color_index(root, xmlns):
    """Read in the list of indexed colors"""
    color_index = []
    colors = root.find(QName(xmlns, 'colors').text)
    if colors is not None:
        indexedColors = colors.find(QName(xmlns, 'indexedColors').text)
        if indexedColors is not None:
            color_nodes = indexedColors.findall(QName(xmlns, 'rgbColor').text)
            for color_node in color_nodes:
                color_index.append(color_node.get('rgb'))
    return color_index

def parse_fonts(root, xmlns, color_index):
    """Read in the fonts"""
    font_list = []
    fonts = root.find(QName(xmlns, 'fonts').text)
    if fonts is not None:
        font_nodes = fonts.findall(QName(xmlns, 'font').text)
        for font_node in font_nodes:
            font = Font()
            font.size = font_node.find(QName(xmlns, 'sz').text).get('val')
            font.name = font_node.find(QName(xmlns, 'name').text).get('val')
            font.bold = True if len(font_node.findall(QName(xmlns, 'b').text)) else False
            font.italic = True if len(font_node.findall(QName(xmlns, 'i').text)) else False
            if len(font_node.findall(QName(xmlns, 'u').text)):
                underline = font_node.find(QName(xmlns, 'u').text).get('val')
                font.underline = underline if underline else 'single'
            color = font_node.find(QName(xmlns, 'color').text)
            if color is not None:
                if color.get('indexed') is not None and 0 <= int(color.get('indexed')) < len(color_index):
                    font.color.index = color_index[int(color.get('indexed'))]
                elif color.get('theme') is not None:
                    if color.get('tint') is not None:
                        font.color.index = 'theme:%s:%s' % (color.get('theme'), color.get('tint'))
                    else:
                        font.color.index = 'theme:%s:' % color.get('theme') # prefix color with theme
                elif color.get('rgb'):
                    font.color.index = color.get('rgb')
            font_list.append(font)
    return font_list

def parse_fills(root, xmlns, color_index):
    """Read in the list of fills"""
    fill_list = []
    fills = root.find(QName(xmlns, 'fills').text)
    count = 0
    if fills is not None:
        fillNodes = fills.findall(QName(xmlns, 'fill').text)
        for fill in fillNodes:
            newFill = Fill()
            # Rotation is unset
            patternFill = fill.find(QName(xmlns, 'patternFill').text)
            if patternFill is not None:
                newFill.fill_type = patternFill.get('patternType')

                fgColor = patternFill.find(QName(xmlns, 'fgColor').text)
                if fgColor is not None:
                    if fgColor.get('indexed') is not None and 0 <= int(fgColor.get('indexed')) < len(color_index):
                        newFill.start_color.index = color_index[int(fgColor.get('indexed'))]
                    elif fgColor.get('theme') is not None:
                        if fgColor.get('tint') is not None:
                            newFill.start_color.index = 'theme:%s:%s' % (fgColor.get('theme'), fgColor.get('tint'))
                        else:
                            newFill.start_color.index = 'theme:%s:' % fgColor.get('theme')  # prefix color with theme
                    else:
                        newFill.start_color.index = fgColor.get('rgb')

                bgColor = patternFill.find(QName(xmlns, 'bgColor').text)
                if bgColor is not None:
                    if bgColor.get('indexed') is not None and 0 <= int(bgColor.get('indexed')) < len(color_index):
                        newFill.end_color.index = color_index[int(bgColor.get('indexed'))]
                    elif bgColor.get('theme') is not None:
                        if bgColor.get('tint') is not None:
                            newFill.end_color.index = 'theme:%s:%s' % (bgColor.get('theme'), bgColor.get('tint'))
                        else:
                            newFill.end_color.index = 'theme:%s:' % bgColor.get('theme')  # prefix color with theme
                    elif bgColor.get('rgb'):
                        newFill.end_color.index = bgColor.get('rgb')
            count += 1
            fill_list.append(newFill)
    return fill_list

def parse_borders(root, xmlns, color_index):
    """Read in the boarders"""
    border_list = []
    borders = root.find(QName(xmlns, 'borders').text)
    if borders is not None:
        boarderNodes = borders.findall(QName(xmlns, 'border').text)
        count = 0
        for boarder in boarderNodes:
            newBorder = Borders()
            if boarder.get('diagonalup') == 1:
                newBorder.diagonal_direction = newBorder.DIAGONAL_UP
            if boarder.get('diagonalDown') == 1:
                if newBorder.diagonal_direction == newBorder.DIAGONAL_UP:
                    newBorder.diagonal_direction = newBorder.DIAGONAL_BOTH
                else:
                    newBorder.diagonal_direction = newBorder.DIAGONAL_DOWN

            for side in ('left', 'right', 'top', 'bottom', 'diagonal'):
                node = boarder.find(QName(xmlns, side).text)
                if node is not None:
                    borderSide = getattr(newBorder,side)
                    if node.get('style') is not None:
                        borderSide.border_style = node.get('style')
                    color = node.find(QName(xmlns, 'color').text)
                    if color is not None:
                        # Ignore 'auto'
                        if color.get('indexed') is not None and 0 <= int(color.get('indexed')) < len(color_index):
                            borderSide.color.index = color_index[int(color.get('indexed'))]
                        elif color.get('theme') is not None:
                            if color.get('tint') is not None:
                                borderSide.color.index = 'theme:%s:%s' % (color.get('theme'), color.get('tint'))
                            else:
                                borderSide.color.index = 'theme:%s:' % color.get('theme') # prefix color with theme
                        elif color.get('rgb'):
                            borderSide.color.index = color.get('rgb')
            count += 1
            border_list.append(newBorder)

    return border_list
